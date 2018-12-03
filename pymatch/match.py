#!/usr/local/bin/env python2
#coding: utf-8
from base import Object

class Match(Object):
    '''
    Match class
    '''
    def __init__(self, val):
        self.__type__ = type(val)


    def __enter__(self):
        return self.__type__


    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
