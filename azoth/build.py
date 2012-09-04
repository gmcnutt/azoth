#!/usr/bin/python

import cPickle
import executor
import obj
from obj import weapon
import place
import session
import sys
import terrain
import terrainmap

sys.path.append('../')

#import hax2
#from hax2 import being, pragma, rules, weapon

sesh = session.Session()

tmap = terrainmap.load_from_nazghul_scm('../haxima/scm/gregors-hut.scm')
sesh.player = obj.Human('Scaramouche')
sesh.world = place.Sector(name='gh', default_terrain=terrain.Grass)
sesh.world.blit_terrain_map(0, 0, tmap)
sesh.hax2.put_being_on_map(sesh.player, sesh.world, 1, 1)

sword = weapon.Sword()
sesh.hax2.put_item_on_map(sword, sesh.world, 3, 3)

savefile = open('start.p', 'w')
cPickle.dump(sesh, savefile)
savefile.close()
