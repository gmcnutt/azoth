#!/usr/bin/python

from azoth import controller, being, executor, weapon, place, session, \
    terrain, terrainmap
import cPickle
import sys

def generate():

    sesh = session.Session()

    tmap = terrainmap.load_from_nazghul_scm('haxima/scm/gregors-hut.scm')
    sesh.world = place.Sector(name='gh', default_terrain=terrain.Grass)
    sesh.world.blit_terrain_map(0, 0, tmap)

    sesh.player = being.Player('Scaramouche')
    sesh.player.controller = controller.Player(sesh.player, sesh)
    sesh.hax2.put_being_on_map(sesh.player, sesh.world, 0, 5)

    sword = weapon.Sword()
    sesh.hax2.put_item_on_map(sword, sesh.world, 3, 3)

    troll = being.Troll('Skoligidornifor')
    troll.controller = controller.Follow(sesh.player, troll, sesh)
    sesh.hax2.put_being_on_map(troll, sesh.world, 0, 6)

    # unicorn = being.Unicorn('Whitey')
    # unicorn.controller = controller.Follow(sesh.player, unicorn, sesh)
    # sesh.hax2.put_being_on_map(unicorn, sesh.world, 0, 7)

    sesh.rules.set_passability('walk', 'wall', executor.PASS_NONE)
    sesh.rules.set_passability('walk', 'boulder', executor.PASS_NONE)
    sesh.rules.set_passability('walk', 'water', executor.PASS_NONE)

    return sesh

if __name__ == "__main__":
    savefile = open('start.p', 'w')
    sesh = generate()
    cPickle.dump(sesh, savefile)
    savefile.close()
