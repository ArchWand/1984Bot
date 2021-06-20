import discord
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
token = os.getenv('discordToken')

bot = commands.Bot(command_prefix=['1984bot, ', '$'])

logChannelID = 851191799464984646

if os.path.exists('rules.csv') == True:
    rulesDF = pd.read_csv('rules.csv', sep=';')
    rulesDF.set_index('index', inplace=True)
else:
    rulesDF = pd.DataFrame(index=(0, 1), columns = ['ID', '1'])
if os.path.exists('blacklist.csv') == True:
    blacklistDF = pd.read_csv('blacklist.csv', sep=';')
    blacklistDF.set_index('index', inplace=True)
else:
    blacklistDF = pd.DataFrame(index=(0, 1, 2), columns = ['ID', 'test'])



blacklistKeywords = ['testing']

@bot.event
async def on_ready():
    print('ONLINE')

'''
DISCORD BOT
- Word Highlight (Maybe find some way to fit into other blacklist too)
- Cone/Kick/Ban message
- Reaction Roles / Role Commands
- Add/Remove blacklist
- Join/Leave message
'''

'''
Blacklist structure
    Message containing blacklist
    File containing blacklist and keywords [class, topic, 'clarification', [keywords]]
        on initialization, all keywords added to a list
    Add command: classification, topic, clarification, keywords
    remove command: class and index/topic
    Edit command: class, topic, revision field 1, etc
        Revision field can be skipped with ^ character
    View command: class, topic; returns keywords
'''

def blEmbedUpdate():
    phobiaEmbed = discord.Embed(title='Phobias', color=discord.Color.dark_theme())
    atEmbed = discord.Embed(title='Avoided Topics', color=discord.Color.dark_theme())
    triggerEmbed = discord.Embed(title='Triggers', color=discord.Color.dark_theme())
    for column in sorted(blacklistDF.columns[1:]):
        if blacklistDF.at[1, column] == 0:
            triggerEmbed.add_field(name=str(column), value=str(blacklistDF.at[0, column]), inline=False)
        if blacklistDF.at[1, column] == 1:
            phobiaEmbed.add_field(name=str(column), value=str(blacklistDF.at[0, column]), inline=False)
        if blacklistDF.at[1, column] == 2:
            atEmbed.add_field(name=str(column), value=str(blacklistDF.at[0, column]), inline=False)
    return triggerEmbed, phobiaEmbed, atEmbed

async def blUpdate(triggerEmbed, phobiaEmbed, atEmbed):
    blChannel = bot.get_channel(int(blacklistDF.columns[0]))
    triggerMsg = await blChannel.fetch_message(id=blacklistDF.at[0, blacklistDF.columns[0]])
    phobiaMsg = await blChannel.fetch_message(id=blacklistDF.at[1, blacklistDF.columns[0]])
    atMsg = await blChannel.fetch_message(id=blacklistDF.at[2, blacklistDF.columns[0]])
    await triggerMsg.edit(embed=triggerEmbed)
    await phobiaMsg.edit(embed=phobiaEmbed)
    await atMsg.edit(embed=atEmbed)
    blacklistDF.to_csv('blacklist.csv', sep=';')

triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
print('BLACKLIST GENERATED')

@bot.command(name='secure', aliases = ['blCreate', 'bC'], help='ENSURE SAFETY OF ENVIRONMENT')
async def blacklistCreator(ctx):
    #print('COMMAND RECEIVED')
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    triggerMsg = await ctx.send(embed=triggerEmbed)
    phobiaMsg = await ctx.send(embed=phobiaEmbed)
    atMsg = await ctx.send(embed=atEmbed)
    blacklistDF.at[0, 'ID'] = triggerMsg.id
    blacklistDF.at[1, 'ID'] = phobiaMsg.id
    blacklistDF.at[2, 'ID'] = atMsg.id
    blacklistDF.rename(columns={'ID': str(ctx.channel.id)}, inplace=True)
    blacklistDF.index.name = 'index'

@bot.command(name='aggregate:', aliases = ['addBL', 'aB'], help='ADD SAFETY PARAMETERS')
async def newBL(ctx, subject, descrip, field, *keywords):
    if field.lower() == 'trigger':
        field = 0
    elif field.lower() == 'phobia':
        field = 1
    elif field.lower() == 'avoided':
        field = 2
    blacklistDF.at[0, subject] = descrip
    blacklistDF.at[1, subject] = field
    for keyword in keywords:
        blacklistKeywords.append(keyword)
    sep = '+'
    keywordJoined = sep.join(keywords)
    blacklistDF.at[2, subject] = keywordJoined
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    await blUpdate(triggerEmbed, phobiaEmbed, atEmbed)

@bot.command(name='diverge:', aliases = ['removeBL', 'rB'], help='REMOVE RESTRICTION')
async def subtractBL(ctx, index):
    keywordJoined = blacklistDF.at[2, index]
    if isinstance(keywordJoined, str) == True:
        keywords = keywordJoined.split('+')
        for keyword in keywords:
            if keyword in blacklistKeywords:
                blacklistKeywords.remove(keyword)
    blacklistDF.pop(index)
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    await blUpdate(triggerEmbed, phobiaEmbed, atEmbed)

'''
Rules structure
    Message containing rules
    Add command: 'rule'(, reindex number)
    Remove command: index
    Edit command: index, 'rule'
'''

def rulesEmbedUpdate():
    rulesEmbed = discord.Embed(title='Rules List', color=discord.Color.dark_theme())
    for column in sorted(rulesDF.columns[1:], key=int):
        rulesEmbed.add_field(name=str(column) + '. ' + str(rulesDF.at[0, column]), value=str(rulesDF.at[1, column]), inline=False)
    return rulesEmbed

async def rulesUpdate(rulesEmbed):
    rulesChannel = bot.get_channel(rulesDF.at[0, 'ID'])
    rulesMsg = await rulesChannel.fetch_message(id=rulesDF.at[1, 'ID'])
    await rulesMsg.edit(embed=rulesEmbed)
    rulesDF.to_csv('rules.csv', sep=';')

rulesEmbed = rulesEmbedUpdate()
print('RULES GENERATED')

@bot.command(name='administrate', aliases = ['rulesCreate', 'rC'], help='ESTABLISH LAW AND ORDER')
async def rulesCreator(ctx):
    #print('COMMAND RECEIVED')
    rulesEmbed = rulesEmbedUpdate()
    rulesMsg = await ctx.send(embed=rulesEmbed)
    rulesDF.at[1, 'ID'] = rulesMsg.id
    rulesDF.at[0, 'ID'] = ctx.channel.id
    rulesDF.index.name = 'index'

@bot.command(name='directive:', aliases = ['addRule', 'aR'], help='EXPAND LEGISLATURE')
async def newRule(ctx, mainRule, descrip, index=None):
    if index == None:
        index = len(rulesDF.columns)
    else:
        index = int(index)
        for column in reversed(rulesDF.columns[index:]):
            rulesDF.rename(columns={column: str(int(column)+1)}, inplace=True)
    rulesDF.at[0, str(index)] = mainRule
    rulesDF.at[1, str(index)] = descrip
    rulesEmbed = rulesEmbedUpdate()
    await rulesUpdate(rulesEmbed)

@bot.command(name='removal:', aliases = ['removeRule', 'rR'], help='STREAMLINE LEGISLATURE')
async def subtractRule(ctx, index):
    rulesDF.pop(index)
    for column in rulesDF.columns[int(index):]:
        rulesDF.rename(columns={column: str(int(column)-1)}, inplace=True)
    rulesEmbed = rulesEmbedUpdate()
    await rulesUpdate(rulesEmbed)
    

'''
Word Highlight
    for keyword in blacklist:
        if msgcontent.contains(keyword):
            violationList.append(keyword)
    send message in mod channel "message (copy) violates these keywords: [violationList]"
'''

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    violationList = []
    logChannel = bot.get_channel(logChannelID)
    for word in blacklistKeywords:
        if word.lower() in message.content.lower():
            violationList.append(word)
    if len(violationList) == 0:
        return
    if len(message.content) < 128:
        violation = message.content
    else:
        violation = 'Violation (Long Message)'
    alert = message.author.name + ' sent a message containing: ' + ', '.join(violationList)
    embed = discord.Embed(title=violation, url=message.jump_url, description=alert, color = discord.Color.dark_gold())
    embed.set_author(name = message.author.name, icon_url=message.author.avatar_url)
    await logChannel.send(embed=embed)

'''
Cone/Ice
    log cone/ice update
    if being added, send message in mod channel "hey! user just got coned/iced! length and reason?"
    upon reply, post reason and punishment in #rulebreaker-central
    set timer for length, automatically remove cone/ice at end
        length can be omitted with ^ character
'''

'''
Kick/ban
    log kick/ban
    send mod channel msg "hey! user got kicked/banned! reason?"
    dm user with reason
'''

'''
Join/Leave
    on join, dm members a copy of the rules
        add string "Randomly placed string to thwart bots! paste this into #shoelace to join" in certain spots randomly
    append user and random string added to list
    a msg from user containing string gives member role and removes them from list
    purge list every 24 hours
    on leave, immortalize their shame.
'''

'''
Reaction Roles
lol no idea how this works
'''

bot.run(token)


    
