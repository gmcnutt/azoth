from nose.tools import *
import unittest

def raises_(exc, func, *args, **kwargs):
    assert_raises(exc, func, *args, **kwargs)

