#!/usr/bin/python2
#coding: utf-8

from pymatch.base import Object


class Trait(Object):
    '''
    Trait type cannot have any instances or objects
    '''
    def __init__(self):
        raise TypeError("Trait type cannot be instantiated")


class Case(Trait):
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
        self.__args__ = args
        self.__is_name_none__ = False
        n = {}
        if names is None:
            self.__is_name_none__ = True
            for i in xrange(0, self.__total__):
                n[i] = i
        else:
            for i in xrange(0, self.__total__):
                n[names[i]] = i
        self.__names__ = n


    @property
    def is_name_none(self):
        return self.__is_name_none__


    def next(self):
        if self.__cnt__ >= self.__total__:
            raise StopIteration
        item = self.__args__[self.__cnt__]
        self.__cnt__ += 1
        return item


    def tail(self):
        if self.__cnt__ >= self.__total__:
            raise StopIteration
        elif self.__cnt__ + 1 == self.__total__:
            return self.next()
        if self.is_name_none is False:
            raise TypeError("named class cannot get remains")
        else:
            return self.__reltype__(*self.__args__[self.__cnt__:])


    def __iter__(self):
        return self

    
    def __getitem__(self, key):
        if self.is_name_none and not isinstance(key, int):
            raise TypeError("key type error! expected [%s], but input is [%s]" % (int, type(key)))
        if not self.__names__.has_key(key):
            raise KeyError("no such key [%s]" % key)
        return self.__args__[self.__names__[key]]
 

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
        def init(self, *args):
            if len(names) == 0:
                Case.__init__(self, None, *args)
            else:
                Case.__init__(self, names, *args)
        cls.__init__ = init
        for base in cls.__bases__:
            if issubclass(base, Case):
                return cls
        cls.__bases__ = (Case, ) + cls.__bases__
        return cls
    return wrapper


def trait(cls):
    '''
    wraps a class to make it a Trait class
    '''
    for base in cls.__bases__:
        if issubclass(base, Trait):
            return cls
    cls.__bases__ = (Trait, ) + cls.__bases__
    return cls