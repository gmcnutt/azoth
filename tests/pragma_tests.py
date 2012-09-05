from nose.tools import *
from azoth import executor
from azoth.obj import baseobject
from azoth.container import Bag, Occupied, Tray
import unittest

def test_bag():
    bag = Bag()
    ok_(not bag)
    x = baseobject.BaseObject()
    bag.put(x)
    ok_(x in bag)
    eq_(1, len(bag))
    ok_(bag)
    bag.put(x)
    eq_(1, len(bag))
    y = baseobject.BaseObject()
    bag.put(y)
    eq_(2, len(bag))
    bag.remove(x)
    ok_(not x in bag)
    bag.remove(y)
    ok_(not bag)

def test_limited_bag():
    bag = Bag(limit=1)
    x = baseobject.BaseObject()
    y = baseobject.BaseObject()
    bag.put(x)
    assert_raises(IndexError, bag.put, y)
    ok_(x in bag)
    ok_(y not in bag)
    bag.remove(x)
    ok_(x not in bag)
    bag.put(y)
    ok_(y in bag)

def test_two_bags():
    bag1 = Bag()
    bag2 = Bag()
    eq_(bag1, bag2)
    x = baseobject.BaseObject()
    y = baseobject.BaseObject()
    bag1.put(x)
    bag2.put(x)
    eq_(bag1, bag2)
    bag1.put(y)
    ok_(bag1 != bag2)
    bag2.put(y)
    eq_(bag1, bag2)

def test_1x1_tray():
    tray = Tray()
    ok_(not tray)
    obj1 = baseobject.BaseObject()
    tray.put(obj1)
    ok_(tray)
    ok_(obj1 in tray)
    obj2 = baseobject.BaseObject()
    assert_raises(IndexError, tray.put, obj2)
    assert_raises(Occupied, tray.insert, 0, 0, obj2)
    assert_raises(IndexError, tray.insert, 0, 1, obj2)
    assert_raises(IndexError, tray.insert, 1, 0, obj2)
    assert_raises(IndexError, tray.insert, 0, -1, obj2)
    assert_raises(IndexError, tray.insert, -1, 0, obj2)
    assert_raises(ValueError, tray.remove, obj2)
    tray.remove(obj1)
    ok_(not tray)
    tray.insert(0, 0, obj2)
    ok_(tray)
    ok_(obj2 in tray)
    eq_((0, 0), tray.index(obj2))
    eq_(obj2, tray.access(0, 0))
    assert_raises(IndexError, tray.access, 0, 1)
    assert_raises(IndexError, tray.access, 1, 0)
    assert_raises(IndexError, tray.access, 0, -1)
    assert_raises(IndexError, tray.access, -1, 0)
    tray.delete(0, 0)
    ok_(not tray)
    tray.delete(0, 0)
    tray.insert(0, 0, obj2)
    tray.clear()
    ok_(not tray)

def test_2x2_tray():
    tray = Tray(2, 2)
    ok_(not tray)
    objects = []
    for i in range(5):
        objects.append(baseobject.BaseObject())

    for i in range(4):
        print(len(tray))
        print(tray)
        tray.put(objects[i])
        ok_(objects[i] in tray)
    eq_(4, len(tray))
    ok_(tray.full)

    assert_raises(IndexError, tray.put, objects[4])
    ok_(objects[4] not in tray)

    assert_raises(Occupied, tray.insert, 0, 0, objects[4])
    assert_raises(IndexError, tray.insert, 0, 2, objects[4])
    assert_raises(IndexError, tray.insert, 2, 0, objects[4])
    assert_raises(IndexError, tray.insert, 0, -1, objects[4])
    assert_raises(IndexError, tray.insert, -1, 0, objects[4])
    assert_raises(ValueError, tray.remove, objects[4])

    assert_raises(IndexError, tray.available)

    x, y = tray.index(objects[0])
    tray.remove(objects[0])
    eq_(3, len(tray))
    ok_(not tray.full)
    eq_((x, y), tray.available())
    tray.insert(x, y, objects[4])
    eq_((x, y), tray.index(objects[4]))

    assert_raises(IndexError, tray.access, 0, 2)
    assert_raises(IndexError, tray.access, 2, 0)
    assert_raises(IndexError, tray.access, 0, -1)
    assert_raises(IndexError, tray.access, -1, 0)

    tray.delete(0, 0)
    eq_(3, len(tray))
    tray.delete(0, 0)
    eq_(3, len(tray))

    tray.clear()
    ok_(not tray)

def test_two_trays():
    tray1 = Tray(2, 2)
    tray2 = Tray(2, 2)
    eq_(tray1, tray2)
    x = baseobject.BaseObject()
    y = baseobject.BaseObject()
    tray1.put(x)
    tray2.put(x)
    eq_(tray1, tray2)
    tray1.put(y)
    ok_(tray1 != tray2)
    tray2.put(y)
    eq_(tray1, tray2)
    
