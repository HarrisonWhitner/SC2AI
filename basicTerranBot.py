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

    # called at the start of the game, used to handle build order
    # def on_start(self):

    # called every step, calls each method necessary for the bot
    async def on_step(self, iteration):

        # define any class variables
        self.step = iteration

        # tasks to do on iteration 0 (at start of match)
        if iteration == 0:

            # create a set of the crucial supply depot locations
            self.supply_init_loc = self.main_base_ramp.corner_depots # | {self.main_base_ramp.depot_in_middle}

        # spread out any idle workers every 10 steps if expanded
        if self.units(COMMANDCENTER).amount > 1 and iteration % 10 == 0:
            await self.distribute_workers()

        # check if workers need to be trained every other step (to avoid double queue bug)
        if iteration % 2 == 0:
            await self.train_workers()

        # check if vespene needs to be built on

        # check if depots need to be built
        await self.build_supply()

        # check if unit buildings need to be built
        await self.build_unit_buildings()

        # check if offensive units need to be trained
        await self.train_offensive_units()

        # check if we should expand


    # determines if workers should be trained, adds them to center's queue if so
    async def train_workers(self):

        # gets every command center that is not already doing something
        for commandCenter in self.units(COMMANDCENTER).ready.noqueue:

            # find if there are any refineries near the command center
            refineries = self.units(REFINERY).closer_than(10.0, commandCenter)

            # find the amount workers assigned to the current command center
            cc_worker_count = commandCenter.assigned_harvesters

            # find the max workers needed for this command center
            cc_worker_max_needed = commandCenter.ideal_harvesters

            # if there are refineries, add their workers into the totals
            if len(refineries) > 0:
                for r in refineries:
                    cc_worker_count += r.assigned_harvesters
                    cc_worker_max_needed += r.ideal_harvesters

            # checks that we can afford a worker and more are needed and enough supply exists
            if self.can_afford(SCV) and self.can_feed(SCV) and cc_worker_count < cc_worker_max_needed:

                # adds a worker to the command center's queue
                await self.do(commandCenter.train(SCV))

    # TODO: come up with a better metric than just less than 2 supply
    # TODO: remove print statements
    # determines if more depots need to be built, starts the build process if so
    async def build_supply(self):

        # TODO: come up with a better metric than just less than 4 supply
        # checks the remaining supply, that we can afford a depot and that one is not already being made
        if self.supply_left <= 3 and self.can_afford(SUPPLYDEPOT) and not self.already_pending(SUPPLYDEPOT):

            # TODO: remove print statement
            print('basicTerranBot: Building a depot at', self.supply_used, 'supply, on step', self.step, 'and time', self.time)

            # build depot at main ramp if not already blocked
            if len(self.supply_init_loc) > 0:
                next_depot_location = self.supply_init_loc.pop()

            # otherwise, build around the top of the main ramp
            else:
                next_depot_location = self.main_base_ramp.upper

            # find a worker to use
            ideal_worker = self.workers.prefer_close_to(next_depot_location).first

            # build depot at the next location
            await self.do(ideal_worker.build(SUPPLYDEPOT, next_depot_location))


    async def build_unit_buildings(self):

        # make sure the first depot is down
        if self.units(SUPPLYDEPOT).amount > 0:

            # builds barracks until there are 3, unless one is not already being built and it cannot be afforded
            if self.units(BARRACKS).amount < 3 and not self.already_pending(BARRACKS) and self.can_afford(BARRACKS):

                # gets the first barracks down on the ramp center
                if self.units(BARRACKS).amount < 1:
                    barracks_location = self.main_base_ramp.barracks_in_middle

                # continues to build barracks near command center until there are 3 total
                else:
                    barracks_location = self.units(COMMANDCENTER).first

                ideal_worker = self.workers.prefer_idle.prefer_close_to(barracks_location).first

                await self.do(ideal_worker.build(BARRACKS, barracks_location))


    # train units for army
    async def train_offensive_units(self):

        # if there is a barracks, train marines
        if self.units(BARRACKS).exists:

            for b in self.units(BARRACKS).ready.noqueue:

                if self.can_afford(MARINE) and self.can_feed(MARINE):

                    await self.do(b.train(MARINE))


""" Code for running a match with my bot """


def main():
    sc2.run_game(
        # the map for the match
        sc2.maps.get("AbyssalReefLE"),
        # list of players, first is my bot, second is an easy SC2 AI
        [ Bot(Race.Terran, basicTerranBot()), Computer(Race.Zerg, Difficulty.Easy) ],
        # set false to run as fast a possible
        realtime=False)


if __name__ == '__main__':
    main()
