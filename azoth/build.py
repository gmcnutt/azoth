#!/usr/bin/python

import cPickle
import session
import sys

sys.path.append('../')

import hax2
from hax2 import being, place, pragma, rules, terrain, terrainmap, \
    weapon

sesh = session.Session()

tmap = terrainmap.load_from_nazghul_scm('../haxima/scm/gregors-hut.scm')
sesh.player = being.Player()
sesh.world = place.Sector(name='gh', default_terrain=terrain.Grass)
sesh.world.blit_terrain_map(0, 0, tmap)
sesh.hax2.put_being_on_map(sesh.player, sesh.world, 10, 10)

sword = weapon.Sword()
sesh.hax2.put_item_on_map(sword, sesh.world, 11, 11)

savefile = open('start.p', 'w')
cPickle.dump(sesh, savefile)
savefile.close()
