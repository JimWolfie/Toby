import json
import time
import hashlib

from Deck_Checker import generate_hashes


class Tournament:
    def __init__ (self, ID, close_date):
        self.players = dict()
        self.games = []
        self.id = ID
        self.close_date = time.strptime(close_date,"%Y-%m-%d %H:%M")
        
    def getPlayers(self):
        return self.players
    def register(self, discord_user, trice_name):
        if time.mktime(time.gmtime()) > time.mktime(self.close_date):
            return "Registration is closed"
        player = Player(discord_user,trice_name)
        self.players[discord_user['id']] = player
        print("{} registered successfully".format(player))

    # def registerPlayer(self, discord_user):
    #     # if discord_user not in self.players:
    #     #     return self.register(self, discord_user, discord_user)
    #     # else:
    #     #     return discord_user
    #     try:
    #         val = self.register(self, discord_user, discord_user)
    #         return val
    #     except KeyError as err:
    #         return "already registered"
        

    def logGame(self, winner, losers):
        winner.points += 3
        players = losers + {winner}
        game = Game(winner, losers, len(self.games)+1)
        for player in players:
            player.games.add(game)
        self.games.add(game)
    def addDeck(self, discord_user, file_location, number):
        player = self.players[discord_user['id']]
        return player.addDeck(file_location, number)
    def setLFG(self, discord_user, value=True):
        try:
            player = self.players[discord_user['id']]
        except KeyError as err:
            return "Player {} not registered.".format(discord_user['name'])
        player.isLFG = value
        if value:
            return "Player {} successfully set as \"looking for group\"".format(discord_user['name'])
        if not value:
            return "Player {} successfully set as \"not looking for group\"".format(discord_user['name'])
                
class Player:
    def __init__(self, user, trice_name):
        self.discord_user = user
        self.trice_name = trice_name
        self.games = []
        self.isLFG = False
        self.decks = dict()
        self.points=0
    
    def addDeck(self, file_location, number):
        hash = generate_hashes.getHash(file_location)
        if not hash[0]:
            return hash[1]
        self.decks[number] = Deck(file_location, hash[1])
        return "Deck {} updated, hash: {}".format(number, hash[1])

class Deck:
    def __init__ (self, file_location, hash):
        self.file_location = file_location
        self.hash = hash
        
class Game:
    def __init__(self, winner, loser_list, id):
        self.losers = loser_list
        self.winner = winner
        self.id = id
    
    def __str__(self):
        str = "Game {}".format(self.id)
        str += "\nWinner: {}".format(self.winner)
        str += "\nLosers:"
        for loser in self.losers:
            str += " {}".format(loser)
        return str
    
class DataBase:
    def __init__(self, file_location="database.json"):
        self.file_location=file_location
        try:
            with open(file_location, "r", encoding="utf-8") as file:
                self.database = json.load(file)
        except IOError:
            self.database = dict()
            database['tournaments']=dict()
            
            print("database file doesn't exist, initializing...")
            with open(file_location, "w", encoding="utf-8") as file:
                json.dump(self.database, file)

    
    def save(self):
        with open(self.file_location, "w", encoding="utf-8") as file:
            json.dump(self.database, file)
        