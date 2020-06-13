# bot.py
import os
import random
import discord
from discord.ext.commands import Bot 
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import requests
import re
import database
import json
import datetime
import argparse

import glob
from discord.ext.commands.converter import MemberConverter



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MAX_DECKS = 3
client = discord.Client()
bot = commands.Bot(command_prefix='?')
close_date = "2020-06-13 12:00"

#db = database.DataBase(r"C:\Users\nlind\Downloads\Trice_Tourney_Utitility\Toby\Trice Tourney Utitility\database.json")
Tourny = database.Tournament(0, close_date)
# Tourny = database.DataBase(self)


@bot.event
# creates a listener
async def on_ready():
    # tells the bot to do the actions under this line whenever the bot starts (whenever the bot "is ready")
    print('------------------------------')
    # a break for organization
    print('Logged in as')
    print(bot.user.name)
    # prints the discord name of the bot
    print(bot.user.id)
    # prints the user id of the bot(these are both just incase something goes wrong and to be a placeholder for
    # organization)
    print('------------------------------')
    print('loading....')
    for i in range(len(bot.guilds)):
        # creates a loop to find the name, size and population of guilds the bot is in
        guild = list(bot.guilds)[i]
        population = len(guild.members)
        size = len(guild.channels)
        print('loading... {0}... has {1} members... has {2} channels... ready...'.format(guild, population, size))
    # end of the loop
    print('------------------------------')
    print(datetime.datetime.now())
    # prints the time the start up finishes
    print('------------------------------')
    
    

@bot.command(name='myID')
async def myID(ctx):
    await ctx.send(ctx.message.author.id)

@bot.command()
async def register(ctx, tricename: str):
    '''?register *trice name*'''
    rawr = ctx.message.author.id
    print(rawr)
    userid = str(ctx.message.author.id)
    uwu = ctx.message.author.name
    print(uwu)
    to_test = Tourny.registerPlayer(uwu, rawr)
    print(to_test)
    t0_test = Tourny.register(to_test,tricename)
    varsity = Tourny.getPlayers
    print("{}".format(varsity))
    with open(r'C:\Users\nlind\Downloads\Trice_Tourney_Utitility\Toby\Trice Tourney Utitility\players.json', "r") as send:
        data = json.load(send)
    if not userid in data:
        
        data[userid] = {}
        data[userid]['trice'] = tricename
        data[userid]['registered'] = ('1')
        print(ctx.message.author.id)
        role = discord.utils.get(ctx.message.guild.roles, name='Competitor')
        await ctx.message.author.add_roles(role)
        await ctx.send('you are now registered')      
    else:
       await ctx.send('you have already registered')
    with open(r'C:\Users\nlind\Downloads\Trice_Tourney_Utitility\Toby\Trice Tourney Utitility\players.json', "w") as send:
        json.dump(data, send, indent=4)

@bot.command(name='getGames')
async def getGames(ctx, user: str):
    players = Tourny.getPlayer(user)
    response = "List of Matching Players and Their Games"
    for player in players:
        response += "\n"+player['name']
        response += "\n Games:"
        for game in player['games']:
            response += "\t "+game.id
    await ctx.send(response)
@bot.command(name='getRanks')
async def getRanks(ctx):
    Tourny
@bot.command(name='saveDeck')
async def getGames(ctx, num: str):
    print(num)
    text = [int(s) for s in num.split() if s.isdigit()][0]  
    print(text)
    number=int(text)
    print(number)
    working = True
    if number > MAX_DECKS or number < 1:
        response = "Invalid Deck Number: Must be between 1 and {}. Could not update {}'s deck.".format(MAX_DECKS,ctx.message.author.name)
        await ctx.send(response)
        await ctx.message.delete()
        working = False
    attaches = ctx.message.attachments
    if not len(attaches) == 1:
        response = "Invalid Number of Decks: You must attach exactly one COD file. Could not update {}'s deck".format(MAX_DECKS,ctx.message.author.name)
        await ctx.send(response)
        await ctx.message.delete()
        working = False
    
    if working:
        dir = "decks/{}-{}/".format(ctx.message.author.name,ctx.message.author.id)
        file_location=dir+"deck {}.cod".format(number)
        
        os.makedirs(dir,exist_ok=True)
        with open(file_location,"wb") as file:
            url = attaches[0].url
            await ctx.message.delete()
            deck = requests.get(url).content
            file.write(deck)
            
        
        response = "Deck {} for {} successfully updated".format(number, ctx.message.author.name)
        await ctx.send(response)
    
    
@bot.command(name='deleteThis')
async def getGames(ctx):
    await ctx.message.delete()

@bot.command(name='LFG')
async def lfg(ctx):
    discord_id = ctx.message.author.id
    discord_name = ctx.message.author.name
    
    vers = Tourny.setLFG(discord_id)
    await vers

@bot.command(name='getHash')
async def convert(ctx, argument):
    try:
        member = await commands.MemberConverter().convert(ctx, argument)
        
        await ctx.send(member.id)
    except commands.BadArgument:
        try:
            return int(argument, base=10)
        except ValueError:
            raise commands.BadArgument(
                f"{argument} is not a valid member or member ID."
            ) from None
            
async def name_to_id(ctx, name):
    server = ctx.message.server
    user_id = server.get_member_named(name).id
    await user_id    
    #get all cod files in dir
    # if working:
    #     path = r'C:\Users\nlind\Downloads\Trice_Tourney_Utitility\Toby'
    #     location = path + 'decks/{}-{}/*'.format(member.name,member.id)
        
    #     for file in glob.glob(location):
    #         try:
    #             nameTuple = generate_hashes.convert_to_deck(file)
    #             delimString = generate_hashes.convert_deck_to_deck_str(nameTuple)
    #             triceHash = generate_hashes.trice_hash(delimString)
    #             await ctx.send('one')
    #             await ctx.send(triceHash)
    #         except:
    #             await ctx.send("End of List :P")
    #         finally:
    #             await ctx.send("hope this helps")



bot.run(TOKEN)    
client.run(TOKEN)
