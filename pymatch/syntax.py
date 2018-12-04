#!/usr/bin/python2
#coding: utf-8

import inspect
import ast
from copy import deepcopy


class TransformWith(ast.NodeTransformer):
    '''
    transform with statement to a regular formal so that we create a syntax sugar for pattern matching

    e.g.
    transform from syntax like belows:
        with Match(a):
            with int:
                <statement_1>
            with str:
                <statement_2>
            with list:
                <statement_3>
            with List as (h, t):
                <statement_4>   # here we can reference to h and t where the former represents the head of list and the later represents the tail of list
            with _:             # match all else
                <statement_5>
    to:
        with Match(a) as t:
            if issubclass(t, int):
                <statement_1>
            elif issubclass(t, str):
                <statement_2>
            elif issubclass(t, list):
                <statement_3>
            elif issubclass(t, List):
                (h, t) = unpack(a, 2)
                <statement_4>
            else:
                <statement_5>
    '''
    def check_match_begin(self, node):
        '''
        check whether node is ```with Match(a) [as t]``` or not
        '''
        if not isinstance(node, ast.With):
            return False
        if not isinstance(node.context_expr, ast.Call):
            return False
        if not isinstance(node.context_expr.func, ast.Name):
            return False
        if node.context_expr.func.id != "Match":
            return False
        return True


    def visit_With(self, node):
        '''
        visit with-context statement
        '''
        if not self.check_match_begin(node):
            return node
        if node.optional_vars is None:
            node.optional_vars = self.do_with_match(node)
        var_name = node.optional_vars.id
        alter_body = []
        pre_sub_with_stmts = None
        for stmt in node.body[::-1]:
            if not isinstance(stmt, ast.With):
                alter_body.append(stmt)
                continue
            if self.check_match_begin(stmt):
                alter_body.append(self.visit_With(stmt))
                continue
            alter_stmt = self.do_with_case(var_name, node.context_expr, stmt, pre_sub_with_stmts)
            if isinstance(alter_stmt, list):
                pre_sub_with_stmts = alter_stmt
            else:
                pre_sub_with_stmts = [alter_stmt]
        alter_body.extend(pre_sub_with_stmts)
        node.body = alter_body[::-1]
        ast.fix_missing_locations(node)
        return node


    def do_with_match(self, node):
        return ast.Name(id="_syntax_sugar_tmp_var", ctx=ast.Store())


    def do_with_case(self, ctx_id, ctx_node, node, orelse):
        if not isinstance(node.context_expr, ast.Name):
            return node
        if orelse is not None and node.context_expr.id == "_":
            raise SyntaxError("any type identifier _ must be at the end of with-statement list")
        # append the last match when it doesn't exist
        if orelse is None and node.context_expr.id != "_":
            orelse = [ast.Raise(
                type=ast.Call(
                    func=ast.Name(id="SyntaxError", ctx=ast.Load()), args=[ast.Str("match nothing!")], keywords=[], starargs=None, kwargs=None
                ), 
                inst=None, tback=None)
            ]
        body = []
        for stmt in node.body:
            if self.check_match_begin(stmt):
                body.append(self.visit_With(stmt))
            else:
                body.append(stmt)
        # convert to if-statement
        if node.optional_vars is not None:
            if isinstance(node.optional_vars, ast.Tuple):
                total = len(node.optional_vars.elts)
            elif isinstance(node.optional_vars, ast.Name):
                total = 1
            else:
                raise SyntaxError("variable capture list must be variable (for only one variable) or tuple (for many variables)")
            assert isinstance(ctx_node, ast.Call)
            ctx_var = ctx_node.args[0].id
            import_stmt = ast.ImportFrom(module="pymatch", names=[ast.alias("unpack", None)], level=0)
            unpack_stmt = ast.Assign(
                targets=[node.optional_vars], 
                value=ast.Call(
                    func=ast.Name(id="unpack", ctx=ast.Load()), 
                    args=[ast.Name(id=ctx_var, ctx=ast.Load()), ast.Num(total)],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                )
            )
            body = [import_stmt, unpack_stmt] + body
        if node.context_expr.id == "_":
            return body
        else:
            return ast.If(
                test = ast.Call(
                    func=ast.Name(id="issubclass", ctx=ast.Load()),
                    args=[ast.Name(id=ctx_id, ctx=ast.Load()), node.context_expr],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                ), 
                body = body,
                orelse = deepcopy(orelse)
            )

    
class TransformFunctionDef(ast.NodeTransformer):
    '''
    remove specify decorates from function definition
    '''
    def visit_FunctionDef(self, node):
        '''
        visit function definition
        '''
        r = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "match":
                continue
            r.append(decorator)
        node.decorator_list = r
        ast.fix_missing_locations(node)
        return node

    
def align_indent(source):
    '''
    indent source code block so as to be used in local code block
    '''
    whitespaces = ['\t', ' ']
    if source[0] not in whitespaces:
        return source
    indent_char = source[0]
    def count_char(source, ch):
        i = 0
        while i < len(source) and source[i] == indent_char:
            i += 1
        return i
    t = source.split("\n")
    total = count_char(source, indent_char)
    r = []
    for item in t:
        if item == '':
            continue
        cnt = count_char(item, indent_char)
        if cnt < total:
            raise IndentationError("unexpected indent")
        r.append((cnt - total) * indent_char + item.lstrip())
    return "\n".join(r)


def chain_transform(tree, transformer_list=[]):
    '''
    transform ast in chains
    '''
    t = tree
    for transformer_type in transformer_list:
        transformer = transformer_type()
        t = transformer.visit(t)
    return t


def match(func):
    '''
    Mark functions whose ast we need to rewrite for pattern matching
    '''
    source = align_indent(inspect.getsource(func))
    tree = ast.parse(source)
    modified = chain_transform(tree, [TransformFunctionDef, TransformWith])
    name = func.__name__
    outer_env = func.__globals__
    def wrap(*args, **kwargs):
        #from test import unparse
        #unparse.Unparser(modified)
        exec compile(modified, '', 'exec') in outer_env
        return outer_env[name](*args, **kwargs)
    return wrap