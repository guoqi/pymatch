#!/usr/bin/python2
#coding: utf-8

import pytest
from ..case import case, trait, unpack, Case, Trait
from ..base import Object


@trait
class Seq(Object) : pass


@case()
class List(Seq) : pass


@trait
class Tree(Object) : pass


@case("left", "right")
class Branch(Tree) : pass


@case("value")
class Leaf(Tree) : pass


class TestCase(object):
    '''
    Test Case class
    '''
    def test_case_with_no_arugment(self):
        '''
        test case function with no argument
        '''
        a = List(1, 2, 3)
        assert type(a) is List
        assert issubclass(List, Case)


    def test_case_with_arguments(self):
        '''
        test case function with two arguments
        '''
        a = Branch(Branch(Leaf(123), Leaf("123")), Leaf(7))
        assert type(a) is Branch
        assert issubclass(Branch, Tree)
        assert issubclass(Branch, Case)
        assert issubclass(Branch, Trait)
        assert not issubclass(Tree, Case)
        assert issubclass(Tree, Trait)
        with pytest.raises(TypeError):
            a = Branch(1, 2, 3)


    def test_unpack(self):
        '''
        test unpack function
        '''
        # test unpack List
        s = List(1, 2, 3, 4)
        (x, y, t) = unpack(s, 3)
        assert x == 1
        assert y == 2
        assert type(t) is List
        (z, w) = unpack(t, 2)
        assert z == 3
        assert w == 4
        # test unpack Tree
        tree = Branch(Branch(Leaf(123), Leaf("123")), Leaf(7))
        (left, right) = unpack(tree, 2)
        assert type(left) is Branch
        assert type(right) is Leaf
        assert right.value == 7
        (left, right) = unpack(left, 2)
        assert type(left) is Leaf
        assert left.value == 123
        assert type(right) is Leaf
        assert right.value == "123"

    
    def test_Case(self):
        tree = Branch(Branch(Leaf(123), Leaf("123")), Leaf(7))
        assert tree.right.value == 7
        assert tree.left.left.value == 123
        assert tree.left.right.value == "123"
        with pytest.raises(AttributeError):
            tree.right = Leaf(8)


    def test_Trait(self):
        with pytest.raises(TypeError):
            a = Tree()