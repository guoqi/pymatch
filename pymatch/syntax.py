#!/usr/bin/python
#coding: utf-8

import inspect
import ast
from pymatch.case import trait


# represent any type
@trait
class _(object): pass


class TransformWith(ast.NodeTransformer):
    '''
    transform with statement to a regular formal so that we create a syntax sugar for pattern matching

    e.g.
    from syntax like belows:
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
    def visit_With(self, node):
        '''
        visit with-context statement
        '''
        if not isinstance(node.context_expr, ast.Call):
            return node
        if not isinstance(node.context_expr.func, ast.Name):
            return node
        if node.context_expr.func.id != "Match":
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
            if pre_sub_with_stmts is None:
                alter_stmt = self.do_with_case(var_name, stmt, stmt.body)
            else:
                alter_stmt = self.do_with_case(var_name, stmt, pre_sub_with_stmts)
            pre_sub_with_stmts.append(alter_stmt)
            alter_body.append(alter_stmt)
        node.body = alter_body
        return node


    def do_with_match(self, node):
        return ast.Name(id="_sytax_sugar_tmp_var", ctx=ast.Store)


    def add_with_finally_stmt(self, body):
        pass


    def do_with_case(self, ctx_id, node, orelse):
        if not isinstance(node.context_expr, ast.Name):
            return node
        if not inspect.isclass(node.context_expr) and node.context_expr.id != "_":
            return node
        # convert to if-statement
        if node.optional_vars is None:
            return ast.If(
                test = ast.Call(
                    func=ast.Name(id="issubclass", ctx=ast.Load),
                    args=[ast.Name(id=ctx_id, ctx=ast.Load), node.context_expr]
                ),
                body = node.body,
                orelse = orelse
            )
        else:
            pass