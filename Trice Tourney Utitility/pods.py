from itertools import combinations,chain
from collections import Counter
from random import shuffle



#arranges players into pods based on currently in queue
def arrangeTables(players, tables, alreadyPaired):
    
    result        = [[]] * tables # list of foursomes
    tableNumber   = 0
    threesomes    = [combinations(range(2,players+1),3)] 
    firstPlayer   = 1     # first player at table (needs 3 opponents)
    placed        = set() # players sitting at tables so far (in result)
    while True:
        opponents = next(threesomes[tableNumber],None)
        if not opponents:
            tableNumber -= 1
            threesomes.pop()
            if tableNumber < 0: return None
            placed.difference_update(result[tableNumber])
            firstPlayer = result[tableNumber][0] 
            continue
        foursome    = [firstPlayer] + list(opponents)
        pairs       = combinations(foursome,2)
        if not alreadyPaired.isdisjoint(pairs): continue
        result[tableNumber] = foursome
        placed.update(foursome)
        tableNumber += 1
        if tableNumber == tables: break
        remainingPlayers = [ p for p in range(1,players+1) if p not in placed ]
        firstPlayer = remainingPlayers[0]
        remainingPlayers = [ p for p in remainingPlayers[1:] if (firstPlayer,p) not in alreadyPaired ]
        threesomes.append(combinations(remainingPlayers,3))       
    return result

def tournamentTables(players):
    tables  = players//4
    rounds  = []    # list of foursome for each round (one foresome per table)
    paired  = set()# player-player tuples (lowest payer number first)
    while True: # len(rounds) < 5
        roundTables = arrangeTables(players,tables,paired)
        if not roundTables: break
        rounds.append(roundTables)
        for foursome in roundTables:
            paired.update(combinations(foursome,2))
    return rounds
v = tournamentTables(16)
print(v)

# def tournamentPods(LFG):
#     if LFG.length < 16:
#         return 
    
#     return rounds
