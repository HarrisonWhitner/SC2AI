"""
My attempt at creating a simple AI bot for Starcraft 2 as the Terran race

Author: Harrison Whitner
Date: 01.24.19

"""


""" Imports """


import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *


""" Code for my SC2 Terran bot """


class basicTerranBot(sc2.BotAI):

    # executed at the start of the game, used to handle build order and actions that need to happen in a specific order
    # def on_start(self):


    # !!! use iteration to keep track of how many times on_step has been called
    # executes every game step, calls each method necessary for the bot on each step
    async def on_step(self, iteration):

        # spread out any idle or unused workers, if iteration is over 200
        if iteration > 400: await self.distribute_workers()

        # update the iteration class variable
        self.iteration = iteration

        # get the total amount of workers, important for the build order
        self.total_worker_count = self.workers.amount

        # get the total amount of depots
        self.total_depot_count = self.units(SUPPLYDEPOT).amount

        # check if workers need to be built
        await self.build_workers()

        # tasks to do on iteration 0 (at start of match)
        if iteration == 0:

            # create a set of the crucial supply depot locations
            self.supply_locations = self.main_base_ramp.corner_depots | {self.main_base_ramp.depot_in_middle}

            # select a random worker to do the building of the first key buildings
            self.first_building_worker = self.workers.random

            # send a random worker to the main base ramp
            await self.do(self.first_building_worker.move(self.main_base_ramp.upper.pop()))

        # check if vespene needs to be built on

        # check if depots need to be built
        await self.build_supply()

        # check if unit buildings need to be built

        # check if offensive units need to be built


    # TODO: fix the two worker being queued problem
    # determines if workers should be built, adds them to center's queue if so
    async def build_workers(self):

        # gets every command center that is not already doing something
        for commandCenter in self.units(COMMANDCENTER).ready.noqueue:

            # TODO: make sure 10 spaces is a reasonable length
            # find the amount workers within 10 spaces the current command center that are collecting minerals
            cc_worker_count = self.workers.closer_than(10.0, commandCenter).collecting.amount

            # find if there are any refineries near the command center
            refineries = self.units(REFINERY).closer_than(10.0, commandCenter)

            # find the max workers needed for this command center
            cc_worker_max_needed = commandCenter.ideal_harvesters

            if len(refineries) > 0:
                for r in refineries:
                    cc_worker_max_needed += r.ideal_harvesters

            # checks that we can afford a worker and more are needed and enough supply exists
            if self.can_afford(SCV) and self.can_feed(SCV) and cc_worker_count < cc_worker_max_needed:

                # adds a worker to the command center's queue
                await self.do(commandCenter.train(SCV))


    # determines if more depots need to be built, starts the build process if so
    async def build_supply(self):

        # TODO: come up with a better metric than just less than 2 supply
        # checks the remaining supply, that we can afford a depot and that one is not already being made
        if self.supply_left < 2 and self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):

            print('Building a depot at', self.supply_used, 'supply, on iteration', self.iteration, 'and time', self.time)

            # try to get depot location from list created at iteration 0
            if len(self.supply_locations) > 0:
                next_depot_location = self.supply_locations.pop()

            # once the crucial walling depots have been made, build further depots near the main ramp
            else:
                next_depot_location = self.main_base_ramp.upper2

            # build depot at the next location
            await self.build(SUPPLYDEPOT, near=next_depot_location)


""" Code for running a match with my bot """


def main():
    sc2.run_game(
        # the map for the match
        sc2.maps.get("AbyssalReefLE"),
        # list of players, first is my bot, second is an easy SC2 AI
        [ Bot(Race.Terran, basicTerranBot()), Computer(Race.Zerg, Difficulty.Easy) ],
        # set false to run as fast a possible
        realtime=True)


if __name__ == '__main__':
    main()
