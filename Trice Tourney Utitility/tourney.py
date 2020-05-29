# import asyncio
# import discord
# from discord.ext import commands
# import argparse
# from random import randint
# import json
# from discord.ext import commands
# import datetime
# from Token import Token

# bot = commands.Bot(command_prefix='?')


# @bot.command()
# async def register(ctx, tricename: str):
#     '''?register *trice name*'''
#     userid = str(ctx.message.author.id)
#     with open('D:\players.json', "r") as send:
#         data = json.load(send)
#     if not userid in data:
#         data[userid] = {}
#         data[userid]['trice'] = tricename
#         data[userid]['registered'] = ('1')
#         print(ctx.message.author.id)
#         role = discord.utils.get(ctx.message.guild.roles, name='Competitor')
#         await ctx.message.author.add_roles(role)
#         await ctx.send('you are now registered')
#     else:
#        await ctx.send('you have already registered')
#     with open('D:\players.json', "w") as send:
#         json.dump(data, send, indent=4)


# bot.run(Token)
