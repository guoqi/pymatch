#!/usr/bin/python2
#coding: utf-8
from pymatch import case, Match, match, Object, trait, unpack

@trait
class Seq(Object): pass

@case()
class List(Seq): pass


@case("left", "right")
class Branch(Object): pass


@case("value")
class Leaf(Object): pass


@match
def foo():
    print List.__bases__
    a = List(1, 2, 3, 4)
    with Match(a):
        with int:
            print "int"
        with str:
            print "str"
        with List as (x, y, tail):
            print x, y, tail
            with Match(tail):
                with int:
                    print "int"
                with List as (z, w):
                    print z, w
                with _:
                    print "no match"
        with _:
            print "no match"


if __name__ == "__main__":
    foo()
    tree = Branch(Leaf(1), Branch(Leaf(2), Leaf(3)))
    print tree.left
    print tree.right
    (left, right) = unpack(tree, 2)
    print left
    print right
    # s = Seq()