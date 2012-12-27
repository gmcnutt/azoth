from tools import *
from azoth import body, armor, slot, weapon

def test_simple():
    head = body.Head()
    helm = armor.Helm()

    head.put(helm)
    ok_(helm in head)
    ok_(head)
    eq_(helm, head.get())
    raises_(slot.OccupiedError, head.put, helm)

    ok_(helm in head) # object
    ok_(armor.Helm in head) # type

    for i in range(2):
        head.clear()
        ok_(not head)
        ok_(not head.get())

    sword = weapon.Sword()
    raises_(slot.WrongContentError, head.put, sword)

