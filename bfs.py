# B R E A D T H   F I R S T   S E A R C H
# Example of using bfs to find the shortest path between graph nodes
# ------------------------------------------------------------------
# This code is derived from one of the homeworks I completed for Peter
# Norvig's *Design of Computer Programs* class on Udacity.com
# Some utility functions provided by Udacity
#
# Problem description:
# --------------------
# Find shortest path (smallest amount of nodes in between) between two
# given stations of Boston subway.
#
# Solution:
# ---------
# First, convert the subway decription into usable form: build a dictionary
# where station names are keys, and values are another dictionaries. Value 
# dictionary consists of all the neighbours of the key station (as keys) and 
# lines that neighbours belong to as values:
# {station:{neighbor:line, ...}, ... } 
# Function subway does that.
# Next, function shortest_path_search performs bfs saving explored paths.
# As soon as path reaches the goal it is returned. Since it's the first one
# found it must be the shortest.
# read more about bfs [here](https://en.wikipedia.org/wiki/Breadth-first_search)

# Imports
import itertools


# Utilities
def subway(**lines):
    """Define a subway map. Input is subway(linename='station1 station2...'...).
    Convert that and return a dict of the form: {station:{neighbor:line,...},...}"""    

    def neighbours(stop, line):
        """ take stop and list of all the stops for the line and return
            neighbours as dict: {stop: N1, N2}"""
        temp = []
        index = line.index(stop)
        if index != 0:
            temp.append(line[index-1])
        if index != len(line) - 1:
            temp.append(line[index+1])
        return (stop, tuple(temp))

    def add_neighbours(nbs, line_name):
        """ take a dict containing stop and it's neighbours and add it to the result dict """
        stop, neighbours = nbs
        for n in neighbours:
            try:
                result[stop][n] = line_name
            except KeyError:
                result[stop] = {n: line_name}
    
    result = {}            
    for line in lines:
        for stop in lines[line].split():
            add_neighbours(neighbours(stop, lines[line].split()), line)
    return result

def path_states(path):
    "Return a list of states in this path."
    return path[0::2]
    
def path_actions(path):
    "Return a list of actions in this path."
    return path[1::2]


# Subway definition
# Insert anything here, but turn off the tests_ride() tests or the program will crash
boston = subway(
    blue='bowdoin government state aquarium maverick airport suffolk revere wonderland',
    orange='oakgrove sullivan haymarket state downtown chinatown tufts backbay foresthills',
    green='lechmere science north haymarket government park copley kenmore newton riverside',
    red='alewife davis porter harvard central mit charles park downtown south umass mattapan')
    
# Solution
# --------
def ride(here, there, system=boston):
    "Return a path on the subway system from here to there."

    def successors(state):
        """Return dict of all possible stops following current one"""
        return system[state]
        
    def is_goal(state):
        """Check if we have reached destination"""
        return state == there

    return shortest_path_search(here, successors, is_goal)


def shortest_path_search(start, successors, is_goal):
    """Find the shortest path from start state to a state
    such that is_goal(state) is true."""
    if is_goal(start):
        return [start]
    explored = set()       # set of states we have visited
    frontier = [ [start] ] # ordered list of paths we have blazed
    while frontier:
        path = frontier.pop(0)
        s = path[-1]
        for (state, action) in successors(s).items():
            if state not in explored:
                explored.add(state)
                path2 = path + [action, state]
                if is_goal(state):
                    return path2
                else:
                    frontier.append(path2)
    return []


# BONUS: find the longest path in the entire system :)
def longest_ride(system):
    """"Return the longest possible path 
    ride between any two stops in the system."""
    return max((ride(here, there) for here, there in itertools.combinations(system.keys(), 2)), key=len)
    #return system.keys()


# Testing results
# Tests provided by Udacity, merci.
def test_ride():
    assert ride('mit', 'government') == [
        'mit', 'red', 'charles', 'red', 'park', 'green', 'government']
    assert ride('mattapan', 'foresthills') == [
        'mattapan', 'red', 'umass', 'red', 'south', 'red', 'downtown',
        'orange', 'chinatown', 'orange', 'tufts', 'orange', 'backbay', 'orange', 'foresthills']
    assert ride('newton', 'alewife') == [
        'newton', 'green', 'kenmore', 'green', 'copley', 'green', 'park', 'red', 'charles', 'red',
        'mit', 'red', 'central', 'red', 'harvard', 'red', 'porter', 'red', 'davis', 'red', 'alewife']
    assert (path_states(longest_ride(boston)) == [
        'wonderland', 'revere', 'suffolk', 'airport', 'maverick', 'aquarium', 'state', 'downtown', 'park',
        'charles', 'mit', 'central', 'harvard', 'porter', 'davis', 'alewife'] or 
        path_states(longest_ride(boston)) == [
                'alewife', 'davis', 'porter', 'harvard', 'central', 'mit', 'charles', 
                'park', 'downtown', 'state', 'aquarium', 'maverick', 'airport', 'suffolk', 'revere', 'wonderland'])
    assert len(path_states(longest_ride(boston))) == 16
    return 'test_ride passes'

def test_subway():
    assert boston['science'] == {'lechmere':'green', 'north':'green'}
    assert boston['state'] == {'government':'blue', 'aquarium':'blue', 'haymarket': 'orange', 'downtown':'orange'}
    assert boston['alewife'] == {'davis':'red'}
    return 'subway fcn is alrigty'

# Print results
print "Shortest ride between copley and oakgrove is:"
print ride('copley', 'oakgrove')

