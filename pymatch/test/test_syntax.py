#!/usr/bin/python2
#coding: utf-8

import ast
import pytest
from ..syntax import TransformWith, TransformFunctionDef, match, align_indent
from ..base import Object
from ..case import case, trait
from ..match import Match


@trait
class Seq(Object) : pass


@case()
class List(Seq) : pass


class TestSyntax(object):
    '''
    Test Syntax class
    '''
    def test_do_with_match(self):
        transformer = TransformWith()
        node = transformer.do_with_match(ast.Name(id="parent", ctx=ast.Load()))
        assert isinstance(node, ast.Name)
        assert node.id == "_syntax_sugar_tmp_var"

    
    def test_do_with_case_without_optional_vars(self):
        '''
        test case:
            with Match(a):
                with int:
                    print "int"
            
        transform to:
            with Match(a):
                if issubclass(t, int):
                    print "str"
                else:
                    raise SyntaxError("match nothing")
        '''
        node = ast.With(
            context_expr = ast.Name(id="int", ctx=ast.Load()),
            optional_vars = None,
            body = [ast.Print(values=ast.Str("int"))]
        )
        ctx_node = ast.Call(
            func = ast.Name(id="Match", ctx=ast.Load()),
            args = [ast.Name(id="a", ctx=ast.Load())],
            keywords = [],
            starargs = None, 
            kwargs = None
        )
        expt = ast.If(
            test = ast.Call(
                func=ast.Name(id="issubclass", ctx=ast.Load()),
                args=[ast.Name(id="t", ctx=ast.Load()), ast.Name(id="int", ctx=ast.Load())],
                keywords=[],
                starargs=None, 
                kwargs=None
            ),
            body = [ast.Print(values=ast.Str("int"))],
            orelse = [ast.Raise(type=ast.Call(func=ast.Name(id="SyntaxError", ctx=ast.Load()), args=[ast.Str("match nothing!")], keywords=[], starargs=None, kwargs=None), 
                                inst=None, tback=None)]
        )
        transformer = TransformWith()
        r = transformer.do_with_case("t", ctx_node, node, None)
        assert ast.dump(expt) == ast.dump(r)
    

    def test_do_with_case_with_optional_vars(self):
        '''
        test case:
            with Match(a):
                with List as (x, y):
                    print "list"
        
        transform to:
            with Match(a):
                if issubclass(t, List):
                    from pymatch import unpack
                    (x, y) = unpack(a, 2)
                    print "List"
                else:
                    a = 123
        '''
        node = ast.With(
            context_expr = ast.Name(id="List", ctx=ast.Load()),
            optional_vars = ast.Tuple(elts=[ast.Name(id="x", ctx=ast.Store()), ast.Name(id="y", ctx=ast.Store())], ctx=ast.Store()),
            body = [ast.Print(values=ast.Str("list"))]
        )
        ctx_node = ast.Call(
            func = ast.Name(id="Match", ctx=ast.Load()),
            args = [ast.Name(id="a", ctx=ast.Load())],
        )
        expt = ast.If(
            test = ast.Call(
                func=ast.Name(id="issubclass", ctx=ast.Load()),
                args=[ast.Name(id="t", ctx=ast.Load()), ast.Name(id="List", ctx=ast.Load())],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            body = [
                ast.ImportFrom(module="pymatch", names=[ast.alias("unpack", None)], level=0),
                ast.Assign(
                    targets=[ast.Tuple(elts=[ast.Name(id="x", ctx=ast.Store()), ast.Name(id="y", ctx=ast.Store())], ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id="unpack", ctx=ast.Load()),
                        args=[ast.Name(id="a", ctx=ast.Load()), ast.Num(2)],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    )
                ), 
                ast.Print(values=ast.Str("list"))
            ],
            orelse = [ast.Assign(ast.Name(id="a", ctx=ast.Store()), ast.Num(123))]
        )
        transformer = TransformWith()
        r = transformer.do_with_case("t", ctx_node, node, [ast.Assign(ast.Name(id="a", ctx=ast.Store()), ast.Num(123))])
        assert ast.dump(expt) == ast.dump(r)


    def test_visit_FunctionDef(self):
        node = ast.FunctionDef(nmae="init", 
                                args=ast.arguments([], None, None, []), 
                                body=[ast.Pass()], 
                                decorator_list=[ast.Name("match", ast.Load())])
        expt = ast.FunctionDef(nmae="init", 
                                args=ast.arguments([], None, None, []), 
                                body=[ast.Pass()], 
                                decorator_list=[])
        transformer = TransformFunctionDef()
        r = transformer.visit_FunctionDef(node)
        assert ast.dump(expt) == ast.dump(r)


    def test_align_indent(self):
        s = "\t\ta\n\t\t\t123\n\t\t8\n\t\t90000\n\t\t\t\t\t\t"
        assert align_indent(s) == "a\n\t123\n8\n90000\n\t\t\t\t"
        s = "\t\t\ta\n\tb\n"
        with pytest.raises(IndentationError):
            align_indent(s)
        s = "ab\n\t123\n\t\t1234\n\tbcd\n\t90\n"
        assert align_indent(s) == "ab\n\t123\n\t\t1234\n\tbcd\n\t90\n"


    def test_match(self):
        @match
        def foo(a):
            with Match(a):
                with int:
                    return "int"
                with str:
                    return "str"
                with List as (x, y, tail):
                    with Match(tail):
                        with List as (z, w):
                            return (x, y, z, w)
        assert foo(List(1, 2, 3, 4)) == (1, 2, 3, 4)