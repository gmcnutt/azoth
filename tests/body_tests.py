from tools import *
from azoth.obj import body, armor, slot, weapon

def test_contains():
    man = body.Humanoid()
    ok_(man.has(body.Head))
    ok_(not man.has(armor.Helm))
    ok_(not man)
    ok_(body.Head in man)
    ok_(not armor.Helm in man)

def test_put():
    man = body.Humanoid()
    helm = armor.Helm()
    man.put(helm)
    ok_(helm in man)
    ok_(armor.Helm in man)
    ok_(man.has(helm))
    ok_(man.has(armor.Helm))

    ok_(man)
    coif = armor.Coif()
    raises_(slot.OccupiedError, man.head.put, coif)
    man.head.remove(helm)
    man.head.put(coif)
    ok_(helm not in man)
    ok_(coif in man)

def test_put2():
    man = body.Humanoid()
    helm = armor.Helm()
    sword = weapon.Sword()
    man.put(helm)
    man.put(sword)
    ok_(helm in man)
    ok_(man.head.has(helm))
    ok_(sword in man)
    ok_(weapon.Sword in man.hands.right)

def test_put_2handed():
    man = body.Humanoid()
    sword = weapon.Sword2H()
    man.put(sword)
    ok_(sword in man)
    ok_(weapon.Sword in man.hands.right)
    ok_(weapon.Sword in man.hands.left)
    man.remove(sword)
    ok_(sword not in man)

def test_replace_2handed():
    man = body.Humanoid()
    sword2h = weapon.Sword2H()
    sword = weapon.Sword()
    shield = armor.Shield()

    man.put(sword2h)
    raises_(slot.OccupiedError, man.put, sword)
    man.remove(sword2h)
    ok_(sword2h not in man)
    man.put(sword)
    ok_(sword in man)
    
    man.put(shield)
    ok_(shield in man)

def test_2h_in_occupied_rhand():
    man = body.Humanoid()
    sword2h = weapon.Sword2H()
    sword = weapon.Sword()
    man.hands.right.put(sword)
    raises_(slot.MultiSlotError, man.hands.right.put, sword2h)
    raises_(slot.OccupiedError, man.hands.put, sword2h)
    man.hands.right.remove(sword)
    man.hands.put(sword2h)
    ok_(sword2h in man.hands.right)
    ok_(sword2h in man.hands.left)

    raises_(slot.MultiSlotError, man.hands.right.remove, sword2h)
    

def test_get():
    man = body.Humanoid()
    helm = armor.Helm()
    man.put(helm)
    eq_(helm, man.head.get())
    ok_(helm in man.get())
