#!/usr/bin/python2
#coding: utf-8

from ..match import Match


class TestMatch(object):
    '''Test Match class
    '''
    def test_init(self):
        '''test Match.__init__
        '''
        match = Match(123)
        assert match.type is int
        match = Match((1, 2))
        assert match.type is tuple


    def test_context(self):
        '''test Match.__enter__ and Match.__exit__
        '''
        with Match([1, 2, 3]) as t:
            assert t is list
