# -*- coding: utf-8 -*-
from django.core.cache import cache
class CalcCache(object):
    '''
        It does use django cache behind the hood
    '''
    @classmethod
    def get(cls, cache_key, key, default = None):
        return cache.get(str(cache_key)+str(key))
    @classmethod
    def set(cls, cache_key, key, value):
        cache.set(str(cache_key)+str(key),value)
        return value
    @classmethod
    def add(cls, cache_key, key, default = None):
        new = cache.add(str(cache_key)+str(key),default)
        return new and default or cls.get(cache_key, key)
    @classmethod
    def get_or_set(cls, cache_key, key, default = None):
        return cls.add(cache_key, key, default = None)
