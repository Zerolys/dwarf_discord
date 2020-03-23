# bot.py
import os
import numpy as np
import discord
import unidecode
import json
from collections import OrderedDict
from affinite import love_compute
import dwarf_factory
from discord.ext import commands
from collections import defaultdict

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'ThePurpleWaleWithBluePschitPchitOnTop'
DATADWARF_FILE = "./dwarf_data.json"

bot = commands.Bot(command_prefix='!')



with open(DATADWARF_FILE) as json_file:
    datadwarf = json.load(json_file)
DWARFGUILD = dwarf_factory.Dwarf_guild(GUILD, datadwarf)

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


@bot.command(name='creuse', help="Mine random")
async def mine(ctx):
    dwarf_author = ctx.author
    dwarf = DWARFGUILD.dwarfs[dwarf_author.id]
    no_error, response = DWARFGUILD.mission_factory[dwarf.current_mission].take_action(
        DWARFGUILD.dwarfs[dwarf._id], DWARFGUILD.dwarfs[dwarf._id].mine_random)
    
    if no_error:
        dict_map = {dwarf.name: bot.get_user(int(dwarf_id)).mention for dwarf_id, dwarf in DWARFGUILD.dwarfs.items()}

        for dwarf_name, dwarf_mention in dict_map.items():
            response = response.replace(dwarf_name, dwarf_mention)

    await ctx.send(response)



@bot.command(name='dwarf', help="Affichage profile")
async def dwarf(ctx, dwarf_mention: discord.Member=None):
    if dwarf_mention is None:
        dwarf = ctx.author
    else:
        dwarf = dwarf_mention

    response = str(DWARFGUILD.dwarfs[dwarf.id])
    
    await ctx.send(response)


@bot.command(name='dwarfguild', help="Affichage profile")
async def dwarf(ctx):
    dwarf_author = ctx.author
    if dwarf_author.id not in DWARFGUILD.dwarfs:
        response = 'YOU ARE NOT EVEN REGISTRREFCD MARGOU DU TROU DU FION ARRETE DE MARGOULINER'
    else:
        response = str(DWARFGUILD)
    
    await ctx.send(response)


@bot.command(name='save', help="Affichage profile")
async def save_data(ctx):

    DWARFGUILD.save_dwarf("./dwarf_data.json")
    response = "Data has been saved."
    await ctx.send(response)


@bot.command(name='deposit', help="Begin Mission")
async def deposit(ctx):

    dwarf_author = ctx.author
    dwarf = DWARFGUILD.dwarfs[dwarf_author.id]
    molly = DWARFGUILD.mission_factory[dwarf.current_mission].molly
    no_error, response = DWARFGUILD.mission_factory[dwarf.current_mission].take_action(
        dwarf, dwarf.deposit_minerals, molly)
    
    if no_error:
        dict_map = {dwarf.name: bot.get_user(int(dwarf_id)).mention for dwarf_id, dwarf in DWARFGUILD.dwarfs.items()}

        for dwarf_name, dwarf_mention in dict_map.items():
            response = response.replace(dwarf_name, dwarf_mention)

    await ctx.send(response)


@bot.command(name='endmission_force', help="Begin Mission")
async def endmission_force(ctx):

    dwarf_author = ctx.author
    current_mission = DWARFGUILD.dwarfs[dwarf_author.id].current_mission
    del DWARFGUILD.mission_factory[current_mission]
    response = "%s mission has ended abruptly." % (current_mission)

    await ctx.send(response)


@bot.command(name='molly', help="Molly profile")
async def molly(ctx):

    dwarf_author = ctx.author
    dwarf = DWARFGUILD.dwarfs[dwarf_author.id]
    molly = DWARFGUILD.mission_factory[dwarf.current_mission].molly
    response = str(molly)
    await ctx.send(response)


@bot.command(name='begin_mission_test', help="Begin Mission")
async def begin_mission(
    ctx,
    mission_name,
    molly_name,
    dwarf_0: discord.Member=None,
    dwarf_1: discord.Member=None,
    dwarf_2: discord.Member=None, 
    dwarf_3: discord.Member=None):

    dwarf_author = ctx.author
    
    if dwarf_author.id not in DWARFGUILD.dwarfs:
        response = 'YOU ARE NOT EVEN REGISTRREFCD MARGOU DU TROU DU FION ARRETE DE MARGOULINER'
    elif dwarf_author.id not in [dwarf.id for dwarf in [dwarf_0, dwarf_1, dwarf_2, dwarf_3] if dwarf is not None]:
        response = "YOU MUST BE ASSIGNED TO THE MISSION"
    else:

        dwarfs = [DWARFGUILD.dwarfs[dwarf.id] for dwarf in [dwarf_0, dwarf_1, dwarf_2, dwarf_3] if dwarf is not None]
        
        response = DWARFGUILD.mission_factory.begin_mission(
            mission_name=mission_name, dwarfs=dwarfs, molly_name=molly_name, clear_condition="nothing", difficulty=1)

        for dwarf in dwarfs:
            if dwarf._my_turn:
                current_dwarf = bot.get_user(int(dwarf._id)).mention

        response += "\n\n[%s] It is %s turn." % (mission_name, current_dwarf)

    await ctx.send(response)

@bot.command(name='addme', help="Begin Mission")
async def addme(ctx, force: int, intelligence: int, dexterity: int, speed: int):
    dwarf = ctx.author

    if dwarf.id not in DWARFGUILD.dwarfs:
        if force + intelligence + dexterity + speed > dwarf_factory.DWARF_SUM_STATS_CAP:
            response = "Impossibulu YOU MORON: SUM OF YOUR STATS SHOULD BE LESS OR EQUAL THAN %s" % dwarf_factory.DWARF_SUM_STATS_CAP
        elif force > dwarf_factory.DWARF_STATS_CAP or intelligence > dwarf_factory.DWARF_STATS_CAP or dexterity > dwarf_factory.DWARF_STATS_CAP or speed > dwarf_factory.DWARF_STATS_CAP:
            response = "Impossibulu YOU MORON: EACH STAT SHOULD BE LESS OR EQYAL THAN %s" % dwarf_factory.DWARF_STATS_CAP
        else:
            DWARFGUILD.add_dwarf(dwarf.id,
                                 dwarf.name,
                                 {"base_force": force,
                                  "base_intelligence": intelligence,
                                  "base_dexterity": dexterity,
                                  "base_speed": speed})
            response = "%s has been added to the %s dwarf city." % (dwarf.name, DWARFGUILD.name)
    else:
        response = "YOU ARE ALREADY REGISTERED BIATVCH"
    
    await ctx.send(response)

bot.run(TOKEN)
