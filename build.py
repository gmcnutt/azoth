#!/usr/bin/python

from azoth import config, controller, being, executor, weapon, place, session, \
    terrain, terrainmap
import cPickle
import os


def generate():

    sesh = session.Session()

    mapfile = os.path.join(config.IMAGE_DIRECTORY, 'haxima', 'worldmap.png')
    tmap = terrainmap.load_from_image(mapfile)
    sesh.world = place.Place(name='world', width=tmap.width, height=tmap.height,
                             default_terrain=terrain.Grass)
    sesh.world.blit_terrain_map(0, 0, tmap)

    sesh.player = being.Player('Scaramouche')
    sesh.player.controller = controller.Player(sesh.player, sesh)
    sesh.hax2.put_being_on_map(sesh.player, sesh.world, 336, 391)

    sword = weapon.Sword()
    sesh.hax2.put_item_on_map(sword, sesh.world, 336, 392)

    troll = being.Troll('Skoligidornifor')
    troll.controller = controller.Follow(sesh.player, troll, sesh)
    sesh.hax2.put_being_on_map(troll, sesh.world, 336, 390)

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
