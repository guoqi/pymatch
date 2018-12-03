#!/usr/local/env python2
#coding: utf-8
from pymatch import case, Match, unpack, Object

@case()
class Seq(Object): pass

@case()
class List(Seq): pass


@case("left", "right")
class Branch(Object): pass


@case("value")
class Leaf(Object): pass


def foo():
    print List.__bases__
    a = List(1, 2, 3, 4)
    with Match(a) as t:
        print List
        print t
        if t is int:
            print "int"
        elif t is str:
            print "str"
        elif t is List:
            (x, y, tail) = unpack(a, 3)
            print x, y, tail
            with Match(tail) as t:
                if t is int:
                    print "int"
                if t is List:
                    (z, w) = unpack(tail, 2)
                    print z, w
                else:
                    print "no match"
        else:
            print "no match"


if __name__ == "__main__":
    foo()
    tree = Branch(Leaf(1), Branch(Leaf(2), Leaf(3)))
    print tree.left
    print tree.right