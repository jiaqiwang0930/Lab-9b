#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 11:23:19 2024

@author: helenwang
"""

from numpy import random, mean
params = {'world_size':(20,20),
          'num_agents':380,
          'same_pref' :0.4,
          'max_iter'  :100,
          'out_path'  :r'c:/users/helenwang/Documents/Github/Lab-9b/simulation.csv' }
class Agent():
    def __init__(self, world, kind, preference):
        self.world = world
        self.kind = kind
        self.preference = preference
        self.location = None

    def move(self):
        vacancies = self.world.find_vacant(return_all=True)
        for patch in vacancies:
            i_moved = True
        pass
class World():
    def __init__(self, params):
        assert(params['world_size'][0] * params['world_size'][1] > params['num_agents']), 'Grid too small for number of agents.'
        self.params = params
        self.reports = {}
        self.grid = self.build_grid(params['world_size'])
        self.agents = self.build_agents(params['num_agents'], params['same_pref'])
        self.init_world()

    def build_grid(self, world_size):
        locations = [(i,j) for i in range(world_size[0]) for j in range(world_size[1])]
        return {l:None for l in locations}

    def build_agents(self, num_agents, same_pref):

        def _kind_picker(i):
            if i < round(num_agents / 2):
                return 'red'
            else:
                return 'blue'

        agents = [Agent(self, _kind_picker(i), same_pref) for i in range(num_agents)]
        random.shuffle(agents)
        return agents

    def init_world(self):
        for agent in self.agents:
            loc = self.find_vacant()
            self.grid[loc] = agent
            agent.location = loc

        assert(all([agent.location is not None for agent in self.agents])), "Some agents don't have homes!"
        assert(sum([occupant is not None for occupant in self.grid.values()]) == self.params['num_agents']), 'Mismatch between number of agents and number of locations with agents.'

        self.reports['integration'] = []

    def find_vacant(self, return_all=False):

        empties = [loc for loc, occupant in self.grid.items() if occupant is None]
        if return_all:
            return empties
        else:
            choice_index = random.choice(range(len(empties)))
            return empties[choice_index]

    def report_integration(self):
        diff_neighbors = []
        for agent in self.agents:
            diff_neighbors.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
        self.reports['integration'].append(round(mean(diff_neighbors), 2))

    def run(self):
        log_of_happy = []
        log_of_moved = []
        log_of_stay  = []

        self.report_integration()
        log_of_happy.append(sum([a.am_i_happy() for a in self.agents]))
        log_of_moved.append(0) 
        log_of_stay.append(0) 

        for iteration in range(self.params['max_iter']):

            random.shuffle(self.agents) 
            move_results = [agent.move() for agent in self.agents]
            self.report_integration()

            num_happy_at_start = sum([r==0 for r in move_results])
            num_moved          = sum([r==1 for r in move_results])
            num_stayed_unhappy = sum([r==2 for r in move_results])

            log_of_happy.append(num_happy_at_start)
            log_of_moved.append(num_moved)
            log_of_stay .append(num_stayed_unhappy)

            if log_of_moved[-1] == log_of_stay[-1] == 0:
                print('Everyone is happy!  Stopping after iteration {}.'.format(iteration))
                break
            elif log_of_moved[-1] == 0 and log_of_stay[-1] > 0:
                print('Some agents are unhappy, but they cannot find anywhere to move to.  Stopping after iteration {}.'.format(iteration))
                break

        self.reports['log_of_happy'] = log_of_happy
        self.reports['log_of_moved'] = log_of_moved
        self.reports['log_of_stay']  = log_of_stay

        self.report()

    def report(self, to_file=True):
        reports = self.reports

        print('\nAll results begin at time=0 and go in order to the end.\n')
        print('The average number of neighbors an agent has not like them:', reports['integration'])
        print('The number of happy agents:', reports['log_of_happy'])
        print('The number of moves per turn:', reports['log_of_moved'])
        print('The number of agents who failed to find a new home:', reports['log_of_stay'])

        if to_file:
            out_path = self.params['out_path']
            with open(out_path, 'w') as f:
                headers = 'turn,integration,num_happy,num_moved,num_stayed\n'
                f.write(headers)
                for i in range(len(reports['log_of_happy'])):
                    line = ','.join([str(i),
                                     str(reports['integration'][i]),
                                     str(reports['log_of_happy'][i]),
                                     str(reports['log_of_moved'][i]),
                                     str(reports['log_of_stay'][i]),
                                     '\n'
                                     ])
                    f.write(line)
            print('\nResults written to:', out_path)
world = World(params)
world.run()
        