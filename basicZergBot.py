"""
My attempt at creating a simple AI bot for Starcraft 2 as the Zerg race

Author: Harrison Whitner
Date: 01.24.19

"""


""" Imports """

import sc2
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.data import Attribute, ActionResult


""" Code for my SC2 Terran bot """

class basicZergBot(sc2.BotAI):

    # executes every game step, calls each method necessary for the bot on each step
    async def on_step(self, iteration):

        # this block is only called once at the start of the game to define variables
        if iteration == 0:

            # sorted list of hatchery location, starting with main at 0 and moving up based on distance from main ramp
            self.hatchery_locations = self.main_base_ramp.bottom_center.sort_by_distance(self.expansion_locations.keys())
            self.hatchery_locations.insert(0, self.start_location)

            # how many extractors are needed at the current time
            self.extractors_needed = 1

            # a list of tasks for the bot to execute in this order
            # task: {'taskType': {'BUILD', 'MOVE', 'RESEARCH'}, 'unitType': 'unit_typeID', 'condition': bool, 'origin': Point2, 'destination': Point2}
            self.task_list = [
            # build a drone at main, send to collect minerals
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            # build an overlord at main, send to the first overlord
            {'taskType': 'BUILD', 'unitType': OVERLORD, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.units(OVERLORD).first.position},
            # build 4 drones at main, send to collect minerals
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            # build spawning pool with a drone from main (building at first overlord, since it spawns on the side farthest from minerals)
            {'taskType': 'BUILD', 'unitType': SPAWNINGPOOL, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.units(OVERLORD).first.position},
            # build a drone at main, send to collect minerals
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            # build hatchery at natural with a drone from main
            {'taskType': 'BUILD', 'unitType': HATCHERY, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[1]},
            # build a drone at main, send to collect minerals
            {'taskType': 'BUILD', 'unitType': DRONE, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.units(MINERALFIELD).closest_to(self.hatchery_locations[0]).position},
            # build extractor at main with drone from main
            {'taskType': 'BUILD', 'unitType': EXTRACTOR, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.vespene_geyser.closest_to(self.hatchery_locations[0]).position}, # maybe need to account for extractors on geysers
            # constantly build workers now, activate train_workers
            # build a 1st queen at main once pool is ready, keep at main
            {'taskType': 'BUILD', 'unitType': QUEEN, 'condition': self.units(SPAWNINGPOOL).exists and self.units(SPAWNINGPOOL).first.is_ready, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            # build 6 zerglings at main, keep at main
            {'taskType': 'BUILD', 'unitType': ZERGLING, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            {'taskType': 'BUILD', 'unitType': ZERGLING, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            {'taskType': 'BUILD', 'unitType': ZERGLING, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            # build 2nd queen at main once pool is ready, keep at main
            {'taskType': 'BUILD', 'unitType': QUEEN, 'condition': self.units(SPAWNINGPOOL).exists and self.units(SPAWNINGPOOL).first.is_ready, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            # 1st queen at main injects main
            # 1st queen at main moves to natural
            # research zergling speed at pool once have 100 gas
            # build 3rd queen at 2nd hatchery, keep at 2nd hatchery
            {'taskType': 'BUILD', 'unitType': QUEEN, 'condition': self.units(HATCHERY).amount >= 2 and all(h.is_ready for h in self.hatcheries), 'origin': self.hatchery_locations[1], 'destination': self.hatchery_locations[0]},
            # move all zerglings at main to scout locations
            # build warren with drone at main once supply @ 44 (building at first overlord, since it spawns on the side farthest from minerals)
            {'taskType': 'BUILD', 'unitType': ROACHWARREN, 'condition': self.supply_used >= 36, 'origin': self.hatchery_locations[0], 'destination': self.units(OVERLORD).first.position}, # TODO: decide between roach or baneling
            # build 3rd hatchery at 3rd expansion with drone at 2nd hatchery once supply @ 44
            {'taskType': 'BUILD', 'unitType': HATCHERY, 'condition': self.supply_used >= 44, 'origin': self.hatchery_locations[1], 'destination': self.get_next_expansion},
            # 3rd queen at natural plants creep tumor at edge of creep near natural
            # train main into lair once supply @ 50
            {'taskType': 'BUILD', 'unitType': LAIR, 'condition': self.supply_used >= 50, 'origin': self.hatchery_locations[0], 'destination': self.hatchery_locations[0]},
            # build evo with drone at main near main once supply @ 50 (building at first overlord, since it spawns on the side farthest from minerals)
            {'taskType': 'BUILD', 'unitType': EVOLUTIONCHAMBER, 'condition': self.supply_used >= 50, 'origin': self.hatchery_locations[0], 'destination': self.units(OVERLORD).first.position},
            # build 2 extractors at main and natural with drone from respective hatchery
            {'taskType': 'BUILD', 'unitType': EXTRACTOR, 'condition': True, 'origin': self.hatchery_locations[0], 'destination': self.state.vespene_geyser.closest_to(self.hatchery_locations[0]).position},
            {'taskType': 'BUILD', 'unitType': EXTRACTOR, 'condition': True, 'origin': self.hatchery_locations[1], 'destination': self.state.vespene_geyser.closest_to(self.hatchery_locations[1]).position},
            # basic zerg into complete, switch over to ai manager now
            ]

            # holds the current task
            self.current_task = None

            # notifies when the iteration 0 setup is done
            print('finished with iteration 0 setup at time', self.time, 'seconds')

        # define a class variable as iteration so that other methods can access it
        self.step = iteration

        # creates buildings and important units in proper order
        await self.task_interpreter()

        """

        # these methods are called every other step, avoids double queue bug
        if iteration % 2 == 0:

            # check if workers need to be trained
            await self.train_workers()

            # check if attacking units need to be trained
            await self.train_attackers()

            # check if supply needs to be built
            await self.build_supply()

        # spread out the workers
        await self.distribute_workers()

        # check if vespene needs to be built on
        await self.build_vespene()

        # check if unit buildings need to be built
        await self.build_unit_buildings()

        # check if tech needs to be upgraded
        await self.upgrade_tech()

        """

    # called every step, tries to complete the first task of the task_list
    async def task_interpreter(self):

        # set result to error so that it is defined
        result = ActionResult.Error

        # if there is no current task, pop the first task off the list and use that
        if self.current_task == None:
            self.current_task = self.task_list.pop(0)

        # check that the current task's condition is met
        if self.current_task['condition']:

            # if the task is to build a unit
            if self.current_task['taskType'] == 'BUILD':

                # check that the unit can be afforded
                if self.can_afford(self.current_task['unitType']):

                    # check if the unit is a structure
                    if Attribute.Structure.value in self._game_data.units[self.current_task['unitType'].value].attributes:

                        # build it at the destination (origin unused)
                        result = await self.build(self.current_task['unitType'], near=self.current_task['destination'])

                    # otherwise the unit is character and needs supply
                    else:

                        # check that there is enough supply for the unit
                        if self.can_feed(self.current_task['unitType']):

                            # check if the unit is a queen
                            if self.current_task['unitType'] == 'QUEEN':

                                # train the queen at the hatchery nearest origin (destination unused)
                                result = await self.do(self.units(HATCHERY).closest_to(self.current_task['origin']).train(self.current_task['unitType']))

                            # else the unit must be a unit morphed from larva
                            else:

                                # check that there is an availabe larva to be morphed from
                                if self.units(LARVA).ready.amount > 0:

                                    # morph the unit from a random larva at the hatchery nearest origin (destination unused)
                                    result = await self.do(self.units(LARVA).closest_to(self.current_task['origin']).train(self.current_task['unitType']))

        # notify what the current task is every 200 steps
        if self.step % 200 == 0:
            print('current task:  result:', result, 'taskType:', self.current_task['taskType'], 'unitType:', self.current_task['unitType'], 'condition:', self.current_task['condition'], 'origin:', self.current_task['origin'], 'destination:', self.current_task['destination'])

        # check to see if the action was executed successfully
        if result == None:

            # print a message notifying that the task was completed (omitted condition because it will always be true)
            print('<> task completed:  taskType:', self.current_task['taskType'], 'unitType:', self.current_task['unitType'], 'origin:', self.current_task['origin'], 'destination:', self.current_task['destination'])

            # set the current task to the next task in task_list
            self.current_task = self.task_list.pop(0)


    # determines if workers should be trained, adds them to base's queue if so
    async def train_workers(self):

        # gets every hatchery
        for h in self.units(HATCHERY):

            # find if there are any extractors
            extractors = self.units(REFINERY).closer_than(10.0, h)

            # find the amount workers assigned to the current hatchery
            worker_count = h.assigned_harvesters

            # find the max workers needed for this hatchery
            worker_max_needed = h.ideal_harvesters

            # if there are extractors, add their workers into the totals
            if len(extractors) > 0:
                for r in extractors:
                    worker_count += r.assigned_harvesters
                    worker_max_needed += r.ideal_harvesters

            # create a list of all larvae at the current hatchery
            larvae = self.units(LARVA).ready.closer_than(5.0, h)

            # checks that we can afford a worker, that more are needed, enough supply exists and larvae exists
            if self.can_afford(DRONE) and self.can_feed(DRONE) and worker_count < worker_max_needed and larvae.amount > 0:

                # adds a worker to the hatchery's queue
                await self.do(larvae.random.train(DRONE))

    # determines if more supply is needed, creates it if so
    async def build_supply(self):

        # checks the remaining supply, that we can afford more supply, that one is not already being made and larvae exists
        if self.supply_left < 3 and self.can_afford(OVERLORD) and not self.already_pending(OVERLORD) and self.units(LARVA).ready.amount > 0:

            # gets a random ready larva from the first hatchery
            larva = self.units(LARVA).ready.closer_than(5.0, self.hatchery_list[0]).random

            # trains a new overlord
            await self.do(larva.train(OVERLORD))

    # builds extractors, amount depending on what type of army
    async def build_vespene(self):

        # if we have less extractors than we need, aren't already building one and can afford one
        if self.extractors_needed > self.units(EXTRACTOR).amount and not self.already_pending(EXTRACTOR) and self.can_afford(EXTRACTOR):

            await self.do(self.select_build_worker().build(EXTRACTOR))

    # builds all buildings needed for units
    async def build_unit_buildings(self):
        return

    # trains attacking units
    async def train_attackers(self):
        return

    # upgrades tech
    async def upgrade_tech(self):
        return


""" Code for running a match with my bot """

def main():
    sc2.run_game(
        # the map for the match
        sc2.maps.get("AbyssalReefLE"),
        # list of players, first is my bot, second is an easy SC2 AI
        [ Bot(Race.Zerg, basicZergBot()), Computer(Race.Terran, Difficulty.Easy) ],
        # set false to run as fast a possible
        realtime=True)

if __name__ == '__main__':
    main()
