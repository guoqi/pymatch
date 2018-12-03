#!/usr/local/env python2
#coding: utf-8
from base import Object

class Case(Object):
    '''
    Case class is available to unpack and pattern matching

    An instance of Case class is always immutable and it also has getter functions whose names are the same as formal arguments
    '''
    def __init__(self, names=None, *args):
        self.__dict__["__iterobj__"] = CaseIterator(self.__class__, names, *args)

    
    def __iter__(self):
        return self.__iterobj__


    def __getattr__(self, name):
        return self.__iterobj__[name]

    
    def __setattr__(self, name, value):
        raise AttributeError("it's not allowed to assign value to attributes of case class")


class CaseIterator(Object):
    '''
    Support lazy iterator so that we could partial unpack an object
    '''
    def __init__(self, reltype, names=None, *args):
        if names is not None and len(names) != len(args):
            raise TypeError("number of parameters doesn't equal the number of arguments")
        self.__reltype__ = reltype
        self.__cnt__ = 0
        self.__total__ = len(args)
        self.__args__ = {}
        self.__is_name_none__ = False
        if names is None:
            self.__is_name_none__ = True
            names = range(0, self.__total__)
        # self.__args__ is a dict where key is argument of definition when names is not None otherwise number
        for (n, a) in zip(names, args):
            self.__args__[n] = a


    @property
    def is_name_none(self):
        return self.__is_name_none__


    def next(self):
        if self.__cnt__ >= self.__total__:
            raise StopIteration
        if self.is_name_none:
            item = self.__args__[self.__cnt__]
        else:
            item = self.__args__.iteritems()[self.__cnt__]
        self.__cnt__ += 1
        return item


    def tail(self):
        if self.__cnt__ >= self.__total__:
            raise StopIteration
        elif self.__cnt__ + 1 == self.__total__:
            return self.next()
        return self.__reltype__(*(self.__args__.values())[self.__cnt__:])


    def __iter__(self):
        return self

    
    def __getitem__(self, key):
        if self.is_name_none and not isinstance(key, int):
            raise TypeError("key type error! expected [%s], but input is [%s]" % (int, type(key)))
        if not self.__args__.has_key(key):
            raise KeyError("no such key [%s]" % key)
        return self.__args__[key]
 

def unpack(val, n):
    '''
    unpack val. val must be instance of LazyIterator type
    '''
    def _unpack(it, n):
        if n == 0:
            raise RuntimeError("no argument for unpacking")
        r = []
        while n > 1:
            h = next(it)
            r.append(h)
            n -= 1
        r.append(it.tail())
        return tuple(r)
    return _unpack(iter(val), n)


def case(*names):
    '''
    wraps a class to make it a Case class and available for pattern matching
    '''
    def wrapper(cls, *args, **kwargs):
        print cls, args, kwargs
        def init(self, *args):
            if len(names) == 0:
                Case.__init__(self, None, *args)
            else:
                Case.__init__(self, names, *args)
        cls.__init__ = init
        cls.__bases__ = (Case, ) + cls.__bases__
        return cls
    return wrapper
