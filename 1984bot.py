import discord
import numpy as np
import pandas as pd
import os
import sys
from dotenv import load_dotenv
from discord.ext import commands
import random
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get
import re
import math

intents = discord.Intents.default()
intents.members = True

load_dotenv()
token = os.getenv('discordToken')

bot = commands.Bot(command_prefix = ['1984bot, ', '$'], intents = intents)

logChannelID = 829010774231744513
shoelaceID = 843198731565662250
memberRoleID = 835601075541245952
ignoredChannels = [808824429824049173, 851848452022992936, 851191799464984646, 856916672941916210]

if os.path.exists('rules.csv') == True:
    rulesDF = pd.read_csv('rules.csv', sep = ';')
    rulesDF.set_index('index', inplace = True)
else:
    rulesDF = pd.DataFrame(index = (0, 1), columns = ['ID', '1'])
if os.path.exists('blacklist.csv') == True:
    blacklistDF = pd.read_csv('blacklist.csv', sep = ';')
    blacklistDF.set_index('index', inplace = True)
else:
    blacklistDF = pd.DataFrame(index = (0, 1, 2), columns = ['ID', 'test'])


newMemberKeys = []
blacklistKeywords = []
blacklistSuggestions = []

for column in blacklistDF.columns[1:]:
    try:
        if math.isnan(blacklistDF.at[2, column]) == True:
            continue
    except:
        keywords = re.split(' ', blacklistDF.at[2, column])
        for word in keywords:
            blacklistKeywords.append(word)

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
    phobiaEmbed = discord.Embed(title = 'Phobias', color = discord.Color.dark_theme())
    atEmbed = discord.Embed(title = 'Avoided Topics', color = discord.Color.dark_theme())
    triggerEmbed = discord.Embed(title = 'Triggers', color = discord.Color.dark_theme())
    for column in sorted(blacklistDF.columns[1:]):
        if blacklistDF.at[1, column] == '0':
            triggerEmbed.add_field(name = str(column), value = str(blacklistDF.at[0, column]), inline = False)
        elif blacklistDF.at[1, column] == '1':
            phobiaEmbed.add_field(name = str(column), value = str(blacklistDF.at[0, column]), inline = False)
        elif blacklistDF.at[1, column] == '2':
            atEmbed.add_field(name = str(column), value = str(blacklistDF.at[0, column]), inline = False)
        else:
            print('FUCKED IT UP')
    return triggerEmbed, phobiaEmbed, atEmbed

async def blUpdate(triggerEmbed, phobiaEmbed, atEmbed):
    blChannel = bot.get_channel(int(blacklistDF.columns[0]))
    triggerMsg = await blChannel.fetch_message(id = blacklistDF.at[0, blacklistDF.columns[0]])
    phobiaMsg = await blChannel.fetch_message(id = blacklistDF.at[1, blacklistDF.columns[0]])
    atMsg = await blChannel.fetch_message(id = blacklistDF.at[2, blacklistDF.columns[0]])
    await triggerMsg.edit(embed = triggerEmbed)
    await phobiaMsg.edit(embed = phobiaEmbed)
    await atMsg.edit(embed = atEmbed)
    blacklistDF.to_csv('blacklist.csv', sep = ';')

triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
print('BLACKLIST GENERATED')

@bot.command(name = 'secure', aliases = ['blCreate', 'bC', 'blacklist', 'blacklistCreate'], help = 'ENSURE SAFETY OF ENVIRONMENT')
@has_permissions(kick_members = True)
async def blacklistCreator(ctx):
    #print('COMMAND RECEIVED')
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    triggerMsg = await ctx.send(embed = triggerEmbed)
    phobiaMsg = await ctx.send(embed = phobiaEmbed)
    atMsg = await ctx.send(embed = atEmbed)
    originalID = blacklistDF.columns[0]
    blacklistDF.rename(columns = {originalID: 'ID'}, inplace = True)
    blacklistDF.at[0, 'ID'] = triggerMsg.id
    blacklistDF.at[1, 'ID'] = phobiaMsg.id
    blacklistDF.at[2, 'ID'] = atMsg.id
    blacklistDF.rename(columns = {'ID': str(ctx.channel.id)}, inplace = True)
    blacklistDF.index.name = 'index'

@bot.command(name = 'aggregate:', aliases = ['addBL', 'aB', 'addBlacklist'], help = 'ADD SAFETY PARAMETERS')
@has_permissions(kick_members = True)
async def newBL(ctx, subject, descrip, field, *keywords):
    if field.lower() == 'trigger':
        field = '0'
    elif field.lower() == 'phobia':
        field = '1'
    elif field.lower() == 'avoided':
        field = '2'
    else:
        raise
    blacklistDF.at[0, subject] = descrip
    blacklistDF.at[1, subject] = field
    for keyword in keywords:
        blacklistKeywords.append(keyword)
    sep = ' '
    keywordJoined = sep.join(keywords)
    blacklistDF.at[2, subject] = keywordJoined
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    await blUpdate(triggerEmbed, phobiaEmbed, atEmbed)

@bot.command(name = 'diverge:', aliases = ['removeBL', 'rB', 'removeBlacklist', 'delBlacklist', 'deleteBlacklist'], help = 'REMOVE RESTRICTION')
@has_permissions(kick_members = True)
async def subtractBL(ctx, index):
    keywordJoined = blacklistDF.at[2, index]
    if isinstance(keywordJoined, str) == True:
        keywords = keywordJoined.split(' ')
        for keyword in keywords:
            if keyword in blacklistKeywords:
                blacklistKeywords.remove(keyword)
    blacklistDF.pop(index)
    triggerEmbed, phobiaEmbed, atEmbed = blEmbedUpdate()
    await blUpdate(triggerEmbed, phobiaEmbed, atEmbed)

@bot.command(name = 'suggest', aliases = ['blS', 'blSuggest', 'blacklistSuggestion'], help = 'COMMUNITY SOURCING')
async def suggestBL(ctx, field, subject, *descrips):
    if field.lower() != 'avoided':
        if field.lower() != 'phobia':
            if field.lower() != 'trigger':
                await ctx.send('Incorrect field type. Reformat.')
                return
    
    blSuggestEmbed = discord.Embed(title = 'New ' + field, color = discord.Color.dark_theme()) 
    sep = ' '
    blSuggestEmbed.add_field(name = subject, value = sep.join(descrips), inline = False)
    blSuggestEmbed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
    logChannel = bot.get_channel(logChannelID)
    message = await logChannel.send(embed = blSuggestEmbed)
    await message.edit(content = str(message.id), embed = blSuggestEmbed)
    blacklistSuggestions.append([message.id, subject, sep.join(descrips), field])

@bot.command(name = 'accept', aliases = ['blAcc', 'blAccept', 'blacklistAccept'], help = 'VALIDATION AND APPROVAL')
@has_permissions(kick_members = True)
async def acceptBL(ctx, ID, *keywords):
    for ticket in blacklistSuggestions:
        if ticket[0] == int(ID):
            await newBL(ctx, ticket[1], ticket[2], ticket[3], *keywords)
            blacklistSuggestions.remove(ticket)
            
'''
Rules structure
    Message containing rules
    Add command: 'rule'(, reindex number)
    Remove command: index
    Edit command: index, 'rule'
'''

def rulesEmbedUpdate():
    rulesEmbed = discord.Embed(title = 'Rules List', color = discord.Color.dark_theme())
    for column in sorted(rulesDF.columns[1:], key = int):
        rulesEmbed.add_field(name = str(column) + '. ' + str(rulesDF.at[0, column]), value = str(rulesDF.at[1, column]), inline = False)
    return rulesEmbed

async def rulesUpdate(rulesEmbed):
    rulesChannel = bot.get_channel(rulesDF.at[0, 'ID'])
    rulesMsg = await rulesChannel.fetch_message(id = rulesDF.at[1, 'ID'])
    await rulesMsg.edit(embed = rulesEmbed)
    rulesDF.to_csv('rules.csv', sep = ';')

rulesEmbed = rulesEmbedUpdate()
print('RULES GENERATED')

@bot.command(name = 'administrate', aliases = ['rulesCreate', 'rC', 'rules'], help = 'ESTABLISH LAW AND ORDER')
@has_permissions(kick_members = True)
async def rulesCreator(ctx):
    #print('COMMAND RECEIVED')
    rulesEmbed = rulesEmbedUpdate()
    rulesMsg = await ctx.send(embed = rulesEmbed)
    rulesDF.at[1, 'ID'] = rulesMsg.id
    rulesDF.at[0, 'ID'] = ctx.channel.id
    rulesDF.index.name = 'index'

@bot.command(name = 'directive:', aliases = ['addRule', 'aR'], help = 'EXPAND LEGISLATURE')
@has_permissions(kick_members = True)
async def newRule(ctx, mainRule, descrip, index = None):
    if index == None:
        index = len(rulesDF.columns)
    else:
        index = int(index)
        for column in reversed(sorted(rulesDF.columns[1:], key = int)[index-1:]):
            rulesDF.rename(columns = {column: str(int(column)+1)}, inplace = True)
    rulesDF.at[0, str(index)] = mainRule
    rulesDF.at[1, str(index)] = descrip
    rulesEmbed = rulesEmbedUpdate()
    await rulesUpdate(rulesEmbed)

@bot.command(name = 'removal:', aliases = ['removeRule', 'rR', 'delRule', 'deleteRule', 'subtractRule'], help = 'STREAMLINE LEGISLATURE')
@has_permissions(kick_members = True)
async def subtractRule(ctx, index):
    rulesDF.pop(index)
    for column in sorted(rulesDF.columns[1:], key = int)[int(index)-1:]:
        rulesDF.rename(columns = {column: str(int(column)-1)}, inplace = True)
    rulesEmbed = rulesEmbedUpdate()
    await rulesUpdate(rulesEmbed)
    

'''
Word Highlight
    for keyword in blacklist:
        if msgcontent.contains(keyword):
            violationList.append(keyword)
    send message in mod channel "message (copy) violates these keywords: [violationList]"
'''

def parseContent(message):
    string = message.content.lower()
    # All below replaces characters in a string (common substitutions) to prevent people from escaping the blacklist
    replaceDict = {
        '\u200B-\u200F\u2028-\u2029\uFEFF': '', # Zero-width characters
        '1': 'i',
        '3': 'e',
        '4': 'a',
        '5': 's',
        'ñ': 'n',
        '7': 't',
        '0': 'o',
        '8': 'b',
        '&': 'and',
        'wanna': 'want to',
        '(?<!yo)ur': 'your',
        '-': ' ',
        '–': ' ',
        '—': ' ',
        '_': ' ',
        ':a:': 'a',
        ':b:': 'b',
        ':o2:': 'o',
        '\U0001f1e6': 'a',
        '\U0001f1e7': 'b',
        '\U0001f1e8': 'c',
        '\U0001f1e9': 'd',
        '\U0001f1ea': 'e',
        '\U0001f1eb': 'f',
        '\U0001f1ec': 'g',
        '\U0001f1ed': 'h',
        '\U0001f1ee': 'i',
        '\U0001f1ef': 'j',
        '\U0001f1f0': 'k',
        '\U0001f1f1': 'l',
        '\U0001f1f2': 'm',
        '\U0001f1f3': 'n',
        '\U0001f1f4': 'o',
        '\U0001f1f5': 'p',
        '\U0001f1f6': 'q',
        '\U0001f1f7': 'r',
        '\U0001f1f8': 's',
        '\U0001f1f9': 't',
        ':regional_indicator_u:': 'u',
        ':regional_indicator_v:': 'v',
        ':regional_indicator_w:': 'w',
        ':regional_indicator_x:': 'x',
        ':regional_indicator_y:': 'y',
        ':regional_indicator_z:': 'z',
        ':star_and_crescent:': 'c',
        ':three:': 'e',
        ':pisces:': 'h',
        ':information_source:': 'i',
        ':one:': 'l',
        ':virgo:': 'm',
        ':scorpius:': 'm',
        ':capricorn:': 'n',
        ':o:': 'o',
        ':zero:': 'o',
        ':parking:': 'p',
        ':five:': 's',
        ':cross:': 't',
        ':orthodox_cross:': 't',
        ':ophiuchus:': 'u',
        ':aries:': 'v',
        ' ': ' ',
        ' ': ' '
    }

    for replaceFrom, replaceTo in replaceDict.items():
        string = re.sub(replaceFrom, replaceTo, string)

    return string

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user or message.author.bot:
        return
    shoelaceChannel = bot.get_channel(shoelaceID)
    if message.channel == shoelaceChannel:
        for pair in newMemberKeys:
            if message.author.id == pair[0]:
                if message.content == str(pair[1]):
                    role = get(message.guild.roles, id = memberRoleID)
                    if role is None: role = get(message.guild.roles, name = 'Member')
                    await message.author.add_roles(role)
                    welcomeEmbed = discord.Embed(title = 'New member', url = message.jump_url, description = 'Welcome to the server, <@!'+str(message.author.id)+'>!', color = discord.Color.dark_gold())
                    welcomeEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
                    await shoelaceChannel.send(embed = welcomeEmbed)
                    newMemberKeys.remove(pair)
                    break
    content = parseContent(message)
    content = re.sub('[^\x20-\x7F]', '', content)
    if 'bep' in content: await message.add_reaction(bot.get_emoji(824743021434241054))
    
    if message.channel.id not in ignoredChannels:
        violationList = []
        logChannel = bot.get_channel(logChannelID)
        for word in blacklistKeywords:
            if word.lower() in content.lower():
                violationList.append(word)
        if len(violationList) > 0:
            violation = content[:128]
            for word in violationList:
                matches = re.findall(word, violation, flags=re.I)
                for match in list(set(matches)):
                    violation = re.sub(match, '['+match+']('+message.jump_url+')', violation)
            if len(content) > 128: violation += '...\n[See more ...](' + message.jump_url + ')'
            alert = message.author.name + ' sent [a message](' + message.jump_url + ') containing: ' + ', '.join(violationList)
            violationEmbed = discord.Embed(title = '**Violation**: ' + ', '.join(violationList), url = message.jump_url, description = violation, color = discord.Color.dark_gold())
            violationEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
            violationEmbed.add_field(name = '\u200b', value = alert, inline = True)
            await logChannel.send(embed = violationEmbed)

@bot.event
async def on_raw_message_edit(payload):
    shoelaceChannel = bot.get_channel(shoelaceID)
    message = await bot.get_channel(payload.channel_id).fetch_message(id = payload.message_id)
    if message.author == bot.user or message.author.bot:
        return
    content = parseContent(message)
    content = re.sub('[^\x20-\x7F]', '', content)
    if 'bep' in content: await message.add_reaction(bot.get_emoji(824743021434241054))
    if message.channel.id not in ignoredChannels:
        violationList = []
        logChannel = bot.get_channel(logChannelID)
        for word in blacklistKeywords:
            if word.lower() in content.lower():
                violationList.append(word)
        if len(violationList) > 0:
            violation = content[:128]
            for word in violationList:
                matches = re.findall(word, violation, flags=re.I)
                for match in list(set(matches)):
                    violation = re.sub(match, '['+match+']('+message.jump_url+')', violation)
            if len(content) > 128: violation += '...\n[See more ...](' + message.jump_url + ')'
            alert = message.author.name + ' edited [a message](' + message.jump_url + ') containing: ' + ', '.join(violationList)
            editViolationEmbed = discord.Embed(title = '**Edit Violation**: ' + ', '.join(violationList), url = message.jump_url, description = violation, color = discord.Color.dark_gold())
            editViolationEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
            editViolationEmbed.add_field(name = '\u200b', value = alert, inline = True)
            await logChannel.send(embed = editViolationEmbed)
    
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

@bot.event
async def on_member_join(member):
    rulesEmbed = discord.Embed(title = 'Rules List', url = 'https://docs.google.com/document/d/1vqxfYxO2mtPh0O7rrgOTUx0UtW3a6vDyXjYclI2n5X8/edit?usp=sharing', color = discord.Color.dark_theme())
    columns = sorted(rulesDF.columns[1:], key = int)
    rand_index = random.randint(0, len(columns)-1)
    randKey = random.randint(1000000, 9999999)
    for index in range(len(columns)):
        if rand_index == index:
            if str(rulesDF.at[1, columns[index]]) == '-----':
                rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = 'To access the server, paste ' + str(randKey), inline = False)
            else:
                rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = str(rulesDF.at[1, columns[index]]) + ' To access the server, paste ' + str(randKey), inline = False)
        else:
            rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = str(rulesDF.at[1, columns[index]]), inline = False)
    newMemberKeys.append([member.id, randKey])
    try: await member.send("Welcome to the Curated Tumblr Discord Server! To ensure you're not a bot, please read over the rules and paste a key hidden in the rules into <#843198731565662250>. Upon doing so, you'll be able to access the rest of the server. Thanks, and have fun!", embed = rulesEmbed)     
    except:
        shoelaceChannel = bot.get_channel(shoelaceID)
        embed = discord.Embed(title = 'Oops!', description = "Looks like you don't have DMs enabled. Please enable them temporarily and rejoin the server.", color = discord.Color.dark_theme())
        embed.set_author(name = member.name, icon_url = member.avatar_url)
        await shoelaceChannel.send(content = '<@'+str(member.id)+'>',embed = embed)

@bot.command(name = 'resend', aliases = ['rS', 'resendWelcome'], help = 'REPEAT DECONTAMINATION PROCEDURES')
async def resend(ctx, ID = None):
    if ID == None:
        member = ctx.author
    else: member = bot.get_user(int(ID))
    rulesEmbed = discord.Embed(title = 'Rules List', url = 'https://docs.google.com/document/d/1vqxfYxO2mtPh0O7rrgOTUx0UtW3a6vDyXjYclI2n5X8/edit?usp=sharing', color = discord.Color.dark_theme())
    columns = sorted(rulesDF.columns[1:], key = int)
    rand_index = random.randint(0, len(columns)-1)
    randKey = random.randint(1000000, 9999999)
    for index in range(len(columns)):
        if rand_index == index:
            if str(rulesDF.at[1, columns[index]]) == '-----':
                rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = 'To access the server, paste ' + str(randKey), inline = False)
            else:
                rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = str(rulesDF.at[1, columns[index]]) + ' To access the server, paste ' + str(randKey), inline = False)
        else:
            rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = str(rulesDF.at[1, columns[index]]), inline = False)
    newMemberKeys.append([member.id, randKey])
    try: await member.send("Welcome to the Curated Tumblr Discord Server! To ensure you're not a bot, please read over the rules and paste a key hidden in the rules into <#843198731565662250>. Upon doing so, you'll be able to access the rest of the server. Thanks, and have fun!", embed = rulesEmbed)     
    except:
        shoelaceChannel = bot.get_channel(shoelaceID)
        brokenEmbed = discord.Embed(title = 'Oops!', description = "Looks like you don't have DMs enabled. Please enable them temporarily and rejoin the server.", color = discord.Color.dark_theme())
        brokenEmbed.set_author(name = member.name, icon_url = member.avatar_url)
        await shoelaceChannel.send(content = '<@'+str(member.id)+'>',embed = brokenEmbed)

@bot.command(name = 'activeKeys', aliases = ['viewActiveNewMemberKeys', 'aK', 'viewKeys'], help = 'DISPLAY NEW MATERIAL')
@has_permissions(kick_members = True)
async def viewKeys(ctx):
    keyEmbed = discord.Embed(title = 'Active New Member Keys:', color = discord.Color.greyple())
    for pair in newMemberKeys:
        keyEmbed.add_field(name = bot.get_user(int(pair[0])).name, value = int(pair[1]), inline = False)
    await ctx.send(embed = keyEmbed)

@bot.event
async def on_member_remove(member):
    welcomeChannel = member.guild.system_channel
    if welcomeChannel is None: welcomeChannel = bot.get_channel("welcome-channel")
    leaveEmbed = discord.Embed(title = 'Goodbye!', description = '<@'+str(member.id)+'> has left us <:whyy:812845017412272128>', color = discord.Color.greyple())
    leaveEmbed.set_author(name = member.name, icon_url = member.avatar_url)
    await welcomeChannel.send(embed = leaveEmbed)

'''
Reaction Roles
lol no idea how this works
'''

@bot.command(name='ping', help = 'MONITOR CONNECTION')
async def ping(ctx):
    await ctx.send('Ping is ' + str(np.round(1000*bot.latency, 2)) + 'ms')

@bot.command(name = 'reload', aliases = ['f5', 'refresh'], help = 'RELOAD')
async def reload(ctx):
    print('RELOADING')
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

@bot.command(name = 'disconnect', aliases = ['dc', 'logoff'], help = 'DEACTIVATE')
@has_permissions(kick_members = True)
async def disconnect(ctx):
    rulesDF.to_csv('rules.csv', sep = ';')
    blacklistDF.to_csv('blacklist.csv', sep = ';')
    await bot.close()

bot.run(token)
