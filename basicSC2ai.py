"""
My attempt at creating a simple AI bot for Starcraft 2 as the terran race

Author: Harrison Whitner
Date: 01.24.19

"""


""" Imports """

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *


""" Code for my sc2 bot """

class basicBot(sc2.BotAI):

    # executes every game step, calls each method necessary for the bot on each step
    async def on_step(self, iteration):

        # spread out the workers
        await self.distribute_workers()

        # get the total amount of workers, important for the build order
        total_worker_count = self.workers.amount

        # check if workers need to be built
        await self.build_workers()

        # check if vespene needs to be built on

        # check if supply needs to be built
        await self.build_supply()

        # check if unit buildings need to be built

        # check if offensive units need to be built

    # determines if workers should be built, adds them to base's queue if so
    async def build_workers(self):

        # gets every base that is not already doing something
        for base in self.units(COMMANDCENTER).ready.noqueue:

            # TODO: make sure 10 spaces is a reasonable length
            # find the amount workers within 10 spaces the current base that are collecting minerals
            base_worker_count = self.workers.closer_than(10.0, base).collecting.amount

            # find if there are any refineries near the base
            refineries = self.units(REFINERY).closer_than(10.0, base)

            # find the max workers needed for this base
            max_workers_needed = base.ideal_harvesters

            if len(refineries) > 0:
                for r in refineries:
                    max_workers_needed += r.ideal_harvesters

            print(max_workers_needed)

            # checks that we can afford a worker and more are needed and enough supply exists
            if self.can_afford(SCV) and self.can_feed(SCV) and base_worker_count < max_workers_needed:

                # adds a worker to the base's queue
                await self.do(base.train(SCV))

    # determines if more suppy needs to be built, starts the build process if so
    async def build_supply(self):

        # TODO: come up with a better metric than just less than 2 supply
        # checks the remaining supply, that we can afford more supply and that one is not already being made
        if self.supply_left < 3 and self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):

            # find viable supply locations
            supply_loc = self.main_base_ramp.corner_depots

            # build supply depots near the ramp
            await self.build(SUPPLYDEPOT, near=supply_loc.pop())

""" Code for running a match with my bot """

def main():
    sc2.run_game(
        # the map for the match
        sc2.maps.get("AbyssalReefLE"),
        # list of players, first is my bot, second is an easy sc2 ai
        [ Bot(Race.Terran, basicBot()), Computer(Race.Zerg, Difficulty.Easy) ],
        # set false to run as fast a possible
        realtime=True)

if __name__ == '__main__':
    main()
