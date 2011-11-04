from nose.tools import *
from azoth.hax2 import weapon
import unittest

def test_sword():
    sword = weapon.Sword()
    eq_(type(sword), weapon.Sword)
