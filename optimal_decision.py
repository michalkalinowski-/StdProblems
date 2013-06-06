from functools import update_wrapper
import random

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

def foxes_and_hens(strategy, foxes=7, hens=45):
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
    
def take5(state):
    "A strategy that waits until there are 5 hens in yard, then gathers."
    (score, yard, cards) = state
    if yard < 5:
        return 'wait'
    else:
        return 'gather'

def average_score(strategy, N=1000):
    return sum(foxes_and_hens(strategy) for _ in range(N)) / float(N)

def superior(A, B=take5):
    "Does strategy A have a higher average score than B, by more than 1.5 point?"
    return average_score(A) - average_score(B) > 1.5

def hens_actions(state):
    """ return a touple of actions possible to execute. When there are no
        hens it's stupid to gather"""
    _, yard, _ = state
    return ('wait', 'gather') if yard else ('wait')        

def p_fox(state):
    """ Compute probability of drawing a fox given a deck of cards"""
    _, _, cards = state
    return cards.count('F')/float(cards.count('H')+cards.count('F')) if cards.count('H') else 1 
    # make sure no division by 0 will take place

def strategy(state):
    """ My ultimate-optimal strategy function """
    def EU(action): return Q(state, action)
    return max(['wait', 'gather'], key=EU)

@memo
def U(state):
    """ Returns utility of the state """
    score, yard, cards = state
    if not len(cards):
        return score + yard
    else:
        return max(Q(state, action, U) for action in ['wait', 'gather'])

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
    
def pop_card(cards):
    """ draw a card and remove it from the deck 
        possible choices for kind are random, H, F """
    card = random.choice(cards)
    cards = cards.replace(card, "", 1)
    return card, cards

def test():
    gather = do('gather', (4, 5, 'F'*4 + 'H'*10))
    assert (gather == (9, 0, 'F'*3 + 'H'*10) or 
            gather == (9, 0, 'F'*4 + 'H'*9))
    
    wait = do('wait', (10, 3, 'FFHH'))
    assert (wait == (10, 4, 'FFH') or
            wait == (10, 0, 'FHH'))
    
    assert superior(strategy)
    return 'tests pass'

def test2():
    error = 0.001
    assert (p_fox((0, 0, 'FFHH')) - 0.5) <= error
    assert (p_fox((0, 0, 'FFFHH')) - 0.75) <= error
    assert set(hens_actions((0, 0,'FFHH'))) == set(('wait'))
    assert set(hens_actions((0, 1,'FFHH'))) == set(('wait', 'gather'))
    print "Hens gathered:", average_score(strategy)
    return "Tests Pass"
    

print test2() 
