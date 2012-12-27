#!/usr/bin/python

import controller
import cPickle
import executor
import being, weapon
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
sesh.world = place.Sector(name='gh', default_terrain=terrain.Grass)
sesh.world.blit_terrain_map(0, 0, tmap)

sesh.player = being.Human('Scaramouche')
sesh.player.controller = controller.Player(sesh.player, sesh)
sesh.hax2.put_being_on_map(sesh.player, sesh.world, 0, 5)

sword = weapon.Sword()
sesh.hax2.put_item_on_map(sword, sesh.world, 3, 3)

troll = being.Troll('Skoligidornifor')
troll.controller = controller.Follow(sesh.player, troll, sesh)
sesh.hax2.put_being_on_map(troll, sesh.world, 0, 6)

savefile = open('start.p', 'w')
cPickle.dump(sesh, savefile)
savefile.close()
