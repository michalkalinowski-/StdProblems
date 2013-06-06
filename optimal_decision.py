# F O X E S   A N D   H E N S
# Example of defining an optimal strategy when playing a game based on a random event
# -----------------------------------------------------------------------------------
# This code is derived from one of the homeworks I completed for Peter Norvig's
# *Design of Computer Programs* class on Udacity.com
# Some utility functions provided by Peter Norvig
#
# Problem description:
# --------------------
# You play a game of Foxes and Hens. Threre is a deck consisting of cards of two different
# kinds: foxes and hens. They're shuffled randomly, but you know how many foxes and hens there
# are. If you draw a Hen you add it to the "yard"(score pending). If you draw a Fox it eats all
# the Hens from the yard (resets pending score). You can decide to collect the hens from the yard
# at any point (you add pending score to your score) but you discard the next card from the deck.
# The goal is to score as many hens as possible.
#
# Solution:
# ---------
# This is a classic *decision under uncertainity* problem so game theory approach is used.
# State consists of number of points, points pending and a collection of cards remaining.
# Function of the Utility of the state is defined recursivly in terms of Quality of actions
# [wait, gather] you can take to advance to the next state. Goal is to arrive to the state
# with max score based on the probability of drawing a Fox.

# Imports
from functools import update_wrapper
import random

# Simple Cashing
def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args refuses to be a dict key
            return f(args)
    _f.cache = cache
    return _f

# Utilities
def pop_card(cards):
    """ draw a card and remove it from the deck 
        possible choices for kind are random, H, F """
    card = random.choice(cards)
    cards = cards.replace(card, "", 1)
    return card, cards

# defines
n_foxes = 7
n_hens = 45

def foxes_and_hens(strategy, foxes=n_foxes, hens=n_hens):
    """Play the game of foxes and hens."""
    # A state is a tuple of (score-so-far, number-of-hens-in-yard, deck-of-cards)
    state = (score, yard, cards) = (0, 0, 'F'*foxes + 'H'*hens)
    while cards:
        action = strategy(state)
        state = (score, yard, cards) = do(action, state)
    return score + yard

def do(action, state):
    "Apply action to state, returning a new state."
    score, yard, cards = state
    card, cards = pop_card(cards)
    if action == 'wait':
        return (score, yard+1, cards) if card == 'H' else (score, 0, cards)
    elif action == 'gather':
        return (score + yard, 0, cards)
    else:
        raise ValueError('Wrong action')
    
# Evaluation of the strategy
def average_score(strategy, N=1000):
    return sum(foxes_and_hens(strategy) for _ in range(N)) / float(N)


# Optimal Solution:
# ----------------

def strategy(state):
    """ My ultimate-optimal strategy function """
    # define Expected Utility as quality of performing an action on a state
    def EU(action): return Q(state, action)
    return max(['wait', 'gather'], key=EU)

@memo
def U(state):
    """ Returns utility of the state """
    score, yard, cards = state
    if not len(cards):
        return score + yard
    else:
        return max(Q(state, action, U) for action in hens_actions(state))

def Q(state, action, fU=U):
    """ Returns quality for a given action """
    (score, yard, cards) = state
    Pfx = p_fox(state)
    if action == 'gather':
        return Pfx * fU((score + yard, 0, cards[1:])) + \
                (1-Pfx) * fU((score + yard, 0, cards[:-1]))
    elif action == 'wait':
        return Pfx * fU((score, 0, cards[1:])) + \
                (1-Pfx) * fU((score, yard +1, cards[:-1]))
    else:
        raise ValueError
    
def p_fox(state):
    """ Compute probability of drawing a fox given a deck of cards"""
    _, _, cards = state
    return cards.count('F')/float(cards.count('H')+cards.count('F')) if cards.count('H') else 1 
    # make sure no division by 0 will take place

def hens_actions(state):
    """ return a touple of actions possible to execute. When there are no
        hens it's useless to gather"""
    _, yard, _ = state
    return ['wait', 'gather'] if yard else ['wait']        

# Testing results
def tests():
    error = 0.001
    assert (p_fox((0, 0, 'FFHH')) - 0.5) <= error
    assert (p_fox((0, 0, 'FFFHH')) - 0.75) <= error
    assert set(hens_actions((0, 0,'FFHH'))) == set(('wait'))
    assert set(hens_actions((0, 1,'FFHH'))) == set(('wait', 'gather'))

    # tests below by Peter Norvig, thanks!
    gather = do('gather', (4, 5, 'F'*4 + 'H'*10))
    assert (gather == (9, 0, 'F'*3 + 'H'*10) or 
            gather == (9, 0, 'F'*4 + 'H'*9))
    
    wait = do('wait', (10, 3, 'FFHH'))
    assert (wait == (10, 4, 'FFH') or
            wait == (10, 0, 'FHH'))

# Print some stuff:
print "Gathered", average_score(strategy), "/", n_hens, "Hens on average"
print "Game played thousand times"
print "Yay!"
