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
        if node.optional_vars is None:
            pass


    def do_with_match(self, node):
        pass


    def do_with_case(self, node):
        pass