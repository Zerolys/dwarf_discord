# bot.py
import os
import numpy as np
import discord
import unidecode
import json
from collections import OrderedDict
from affinite import love_compute
from dwarf_factory import Dwarf_guild
from discord.ext import commands
from collections import defaultdict

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'ThePurpleWaleWithBluePschitPchitOnTop'
DATADWARF_FILE = "./dwarf_data.json"

bot = commands.Bot(command_prefix='!')



with open(DATADWARF_FILE) as json_file:
    datadwarf = json.load(json_file)
DWARFGUILD = Dwarf_guild(GUILD, datadwarf)

# @bot.event
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    channel = discord.utils.get(bot.get_all_channels(), guild__name=GUILD, name='der-general')
    casimir = discord.utils.get(bot.get_all_members(), guild__name=GUILD, name='Casimir')
    #for i in range(10):
    #    a = input()
    #    await channel.send(str(casimir.mention) + " " + a)
    # await client.send_message(channel, "OYE MES DWARF!")
    print(f'{bot.user} has connected to Discord!')


@bot.command(name='affinite', help="Affinite entre deux personnes selon un critere")
async def compute_relation(ctx, user1: str, user2: str, word: str):
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    data = OrderedDict(
        name_1=user1,
        name_2=user2,
        word=word
    )
    for key, value in data.items():
        if "@" in value and value[3:-1].isdigit():
            new_value = bot.get_user(int(value[3:-1]))
            if new_value is None:
                new_value = guild.get_role(int(value[3:-1]))
            if new_value is None:
                new_value = value
            else:
                new_value = new_value.name
            data[key] = new_value
    output = love_compute(**data, normalize=True)
    await ctx.send(output)


@bot.command(name='creuse', help="Mine random, amount max: 5")
async def mine(ctx, amount:int = 1):
    dwarf = ctx.author

    if dwarf.id not in DWARFGUILD:
        DWARFGUILD.add_dwarf(dwarf.id, dwarf.name)
    
    if amount >= 5:
        amount = 5
    elif amount < 1:
        amount = 1
    for _ in range(amount):
        response = DWARFGUILD[dwarf.id].mine_random(verbose=True)    
        await ctx.send(response)

@bot.command(name='dwarf', help="Affichage profile")
async def dwarf(ctx):
    dwarf = ctx.author

    if dwarf.id not in DWARFGUILD:
        print("yay")
        DWARFGUILD.add_dwarf(dwarf.id, dwarf.name)
    response = str(DWARFGUILD[dwarf.id])
    
    await ctx.send(response)

bot.run(TOKEN)
