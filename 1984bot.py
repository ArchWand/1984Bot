import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get
from datetime import datetime
from datetime import timedelta
import dateparser
import time
import pandas as pd
import numpy as np
import random
import math
import sys
import os
import re
import asyncio

from musicAdv import Music

load_dotenv()
token = os.getenv('discordToken')

recentIDsPMA = {}
recentIDsAMA = {}
reactRemove = False

recentIDsLandmine = {}
landmines = {}


def expMess(author):
    name = author.mention
    msg = random.choice([
                        f"{name} https://cdn.discordapp.com/attachments/735199144578252930/1432436562343231540/fish_2.mp4",
                        f"{name} stepped on a landmine!",
                        f"{name} exploded.",
                        f"{name} turned into a pile of flesh.",
                        f"{name} got got.",
                        f"{name} tried to rocketjump without gunboats.",
                        f"{name} ceased to exist.",
                        f"{name} uhhhhhhhhhhhhhhhh y'know.",
                        f"{name} was killed by [[Intentional Game Design]](https://bugs.mojang.com/browse/MCPE-28723)",
                        "death.fell.accident.water",
                        f"{name} went off with a bang",
                        f"{name} was obliterated by a sonically-charged landmine",
                        f"{name} shattered into pieces.",
                        f"{name} can't be put back together again.",
                        f"{name} needs to be swept up.",
                        f"{name} just became another dirt pile.",
                        f"That was definitely not {name}'s fault.",
                        f"That was definitely {name}'s fault.",
                        f"{name} died painlessly.",
                        f"{name}'s death was extremely painful.",
                        f"{name} has broken every bone in their body.",
                        f"{name} dies a slightly embarassing death.",
                        f"{name} dies in a hilarious pose.",
                        f"{name} https://tenor.com/view/heavy-tf2-team-fortress-2-heavy-weapons-guy-dead-death-gif-9045752817451426578",
                        f"{name} https://tenor.com/view/cavif-cavifax-gif-3330778137757269524",
                        f"{name} got splatted by an Ink Mine!",
                        f"{name} tried messing with swamp dragons.",
                        f"{name} https://tenor.com/view/dr-manhattan-gif-18899941",
                        f"The assassins finally got to {name}.",
                        f"{name} did an oopsie daisy.",
                        f"{name} got Plok'd.",
                        f"{name} asked who Steve Jobs was.",
                        f"{name} was actually a firework.",
                        f"{name} tried shooting 9 stickies without the Scottish Resistance.",
                        f"{name} https://tenor.com/view/rin-tohsaka-shirou-emiya-fate-stay-night-unlimited-blade-works-explosion-gif-23846246",
                        f"{name} https://tenor.com/view/pipe-bomb-so-cool-pipe-bomb-hatsune-miku-gif-3979886170462943769",
                        f"{name} https://media.discordapp.net/attachments/809108951387340871/1228533347714596935/exploder.gif",
                        f"{name} fell down the stairs! https://images-ext-1.discordapp.net/external/on-YZ-bLmwKqcNmplVusQPs_ZCBMrxdc1fM-qkThfE0/https/media.tenor.com/GZXMiGmk-7kAAAPo/anime-falling.mp4",
                        f"{name} took a tumble down the stairs! https://tenor.com/view/castlevania-godbrand-loop-spiral-staircase-staircase-gif-20125067",
                        f"{name} https://tenor.com/view/reverse-asdfmovie-gif-20767004",
                        f"{name} https://cdn.discordapp.com/attachments/1432022276248834079/1432618182333566976/explode.gif",
                        f"{name} got thrown down the stairs! https://c.tenor.com/wLF96iHtUkMAAAAC/tenor.gif",
                        f"{name} is soaring through the air! They're like a little bird! ^_^ https://cdn.nekotina.com/images/gnFyNt5VR.gif",
                        f"{name} was transformed into a wild beast! https://cdn.discordapp.com/attachments/1432022276248834079/1432618850448314469/2161762323_983946a7ca_o.png",
                        f"{name} was crucified! https://cdn.discordapp.com/attachments/1432022276248834079/1432619979173400668/Crucifixion_Strasbourg_Unterlinden_Inv88RP536.png",
                        f"{name} was struck with divine madness!",
                        f"{name} learned the true nature of things!",
                        f"{name} has gone outside! As should the rest of you!",
                        f"{name} https://cdn.discordapp.com/attachments/961036258463858688/1432642546848366642/squidwardfuckingdies.mp4"
                        ]
    )
    return msg

async def mainBot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.members = True


    bot = commands.Bot(command_prefix = ['1984bot, ', '$'], intents = intents)

    rulesFilePath = 'rules.csv'
    blacklistFilePath = 'blacklist.csv'
    violationsFilePath = 'violations.csv'

    if os.path.exists(rulesFilePath) == True:
        rulesDF = pd.read_csv(rulesFilePath, sep = ';')
        rulesDF.set_index('index', inplace = True)
    else:
        rulesDF = pd.DataFrame(index = range(2), columns = ['ID', '1'])
    if os.path.exists(blacklistFilePath) == True:
        blacklistDF = pd.read_csv(blacklistFilePath, sep = ';')
        blacklistDF.set_index('index', inplace = True)
    else:
        blacklistDF = pd.DataFrame(index = range(3), columns = ['ID', 'test'])
    if os.path.exists(violationsFilePath):
        violationDF = pd.read_csv(violationsFilePath)
        violationDF.set_index('Violation', inplace = True)
    else:
        violationDF = pd.DataFrame(index = range(3), columns = ('Violation', 'Priority', 'Pattern'))

    blacklistSuggestions = []

    nick = os.path.splitext(sys.argv[0])[0]

    @bot.event
    async def on_ready():
        print('ONLINE')
        global ctds, welcomeChannel, logChannel, shoelaceChannel, memberRole, ignoredChannelsID, noUptumblrID, ignoredChannels, noUptumblr, serverDate, chewtoyRole, landmineChannel, validLandmineChannels
        ctds = bot.get_guild(808811670327263312)
        serverDate = ctds.created_at
        welcomeChannel = ctds.system_channel
        if welcomeChannel is None: welcomeChannel = bot.get_channel("welcome-channel")
        logChannel = bot.get_channel(829010774231744513)
        shoelaceChannel = bot.get_channel(843198731565662250)
        landmineChannel = bot.get_channel(825738430326636554)
        memberRole = ctds.get_role(835601075541245952)
        chewtoyRole = ctds.get_role(1424110502149361816)
        ignoredChannels = [808824429824049173, 851848452022992936, 851191799464984646, 856916672941916210, 822836922036387880, 854814653880598528, 864181609354756127]
        noUptumblr = [813499480518426624, 809854730632691712, 854814653880598528]
        
        validCategories = [1293044771324952647, 808899650530050109, 808819803258355813, 811721715084034108, 848677493790605332, 808812095045894244]
        validLandmineChannels = []
        for chnl in ctds.channels:
            if (isinstance(chnl, discord.TextChannel) or isinstance(chnl, discord.ForumChannel)):
                if chnl.category.id in validCategories or chnl.id == 808818440629518376:
                    if chnl.id not in [854814653880598528, 809854730632691712]:
                        validLandmineChannels.append(chnl.id)

        print('VARS DECLARED')

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
        triggerMsg = await blChannel.fetch_message(blacklistDF.at[0, blacklistDF.columns[0]])
        phobiaMsg = await blChannel.fetch_message(blacklistDF.at[1, blacklistDF.columns[0]])
        atMsg = await blChannel.fetch_message(blacklistDF.at[2, blacklistDF.columns[0]])
        await triggerMsg.edit(embed = triggerEmbed)
        await phobiaMsg.edit(embed = phobiaEmbed)
        await atMsg.edit(embed = atEmbed)
        blacklistDF.to_csv(blacklistFilePath, sep = ';')

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
        blSuggestEmbed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar.url)
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
        for column in rulesDF.columns[1:]:
            rulesEmbed.add_field(name = str(column) + '. ' + str(rulesDF.at[0, column]), value = str(rulesDF.at[1, column]), inline = False)
        return rulesEmbed

    async def rulesUpdate(rulesEmbed):
        rulesChannel = bot.get_channel(rulesDF.at[0, 'ID'])
        rulesMsg = await rulesChannel.fetch_message(rulesDF.at[1, 'ID'])
        await rulesMsg.edit(embed = rulesEmbed)
        rulesDF.to_csv(rulesFilePath, sep = ';')

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

    async def indoctrination(message):
        if not message.channel == shoelaceChannel: return
        if message.content == str(userKey(message.author)):
            await message.author.add_roles(memberRole)
            welcomeEmbed = discord.Embed(title = 'New member', url = message.jump_url, description = f'Welcome to the server, {message.author.mention}!', color = discord.Color.dark_gold())
            welcomeEmbed.set_author(name = message.author.name, icon_url = message.author.avatar.url)
            await shoelaceChannel.send(embed = welcomeEmbed)
            await message.add_reaction("<:1984bot:890711017141706792>")
        elif memberRole not in message.author.roles:
            print(f'MESSAGE "{message.content}" NOT EQUIVALENT TO USERKEY {userKey(message.author)}')

    async def randUptumblr(message):
        if message.channel.id in noUptumblr: return
        if random.random() < 0.0001:
            await message.add_reaction("<:uptumblr:810019271215677441>")

    async def beppening(message):
        content = parseContent(message.content)
        if 'bep' in content: await message.add_reaction(bot.get_emoji(824743021434241054))
        if 'joe' in content: await message.add_reaction(bot.get_emoji(1403205405399584909))
        if 'stephanie' in content: await message.add_reaction(bot.get_emoji(1403205409036304456))
        if 'mizraim' in content: await message.add_reaction(bot.get_emoji(1403205407719161907))
        if 'daniel' in content: await message.add_reaction(bot.get_emoji(1403205403424194641))


    def parseContent(string):
        string = string.lower()
        # All below replaces characters in a string (common substitutions) to prevent people from escaping the blacklist
        replaceDict = {
            # '[\u200B-\u200F\u2028-\u2029\uFEFF]': '', # Zero-width characters
            '\u200B': '',
            '1': 'i',
            '3': 'e',
            '4': 'a',
            '5': 's',
            'ñ': 'n',
            '7': 't',
            '0': 'o',
            '8': 'b',
            '&': 'and',
            #'wanna': 'want to',
            #r'\bur': 'your',
            '\U0001F447': 'your',
            '-': ' ',
            '–': ' ',
            '—': ' ',
            '_': ' ',
            '\U0001f170': 'a',
            '\U0001f171': 'b',
            '\U0001f17e': 'o',
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
            '\U0001f1fa': 'u',
            '\U0001f1fb': 'v',
            '\U0001f1fc': 'w',
            '\U0001f1fd': 'x',
            '\U0001f1fe': 'y',
            '\U0001f1ff': 'z',
            '\u262a': 'c',
            '\u2653': 'h',
            '\u2139': 'i',
            '\u264d': 'm',
            '\u264f': 'm',
            '\u2651': 'n',
            '\u2b55': 'o',
            '\U0001f17f': 'p',
            '\u271d': 't',
            '\u2626': 't',
            '\u26ce': 'u',
            '\u2648': 'v',
            ' ': ' ',
            ' ': ' ',
            # '[^\xA\x20-\x7F]': ''
        }

        # for replaceFrom, replaceTo in replaceDict.items():
            # string = re.sub(replaceFrom, replaceTo, string)
        # return string
        
        out = ''
        for letter in string:
            if letter in replaceDict:
                letter = replaceDict[letter]
            out += letter
        return re.sub('[^\x20-\x7F]', '', out)

    def highlight(text, patterns: list, prefix = '', suffix = ''):
        if isinstance(patterns, str): patterns = [patterns]
        iHighlight = {}
        for pattern in patterns:
            prev = False
            for i in range(len(text)):
                match = re.match(pattern, parseContent(text[i:]))
                if match:
                    if not prev:
                        tgtLen = match.end() - match.start()
                        iHighlight[i] = len(text)
                        parseLen = len(parseContent(text[i:iHighlight[i]]))
                        while tgtLen != parseLen:
                            iHighlight[i] = iHighlight[i] - 1
                            parseLen = len(parseContent(text[i:iHighlight[i]]))
                        
                    prev = True
                    continue
                prev = False
        
        for key in sorted(iHighlight, reverse = True):
            toAdd = prefix + text[key:iHighlight[key]] + suffix
            text = text[:key] + toAdd + text[iHighlight[key]:]
        return text

    async def logViolation(message, fromEvent = 'sent'):
        if message.channel.id in ignoredChannels: return
        channel = logChannel
        content = parseContent(message.content)
        
        violationList = []
        containedWords = set()
        
        priority = 0
        for violation in violationDF.index:
            found = re.findall(violationDF.loc[violation, 'Pattern'], content)
            if found:
                violationList.append(violation)
                priority = max(priority, violationDF.loc[violation, 'Priority'])
                containedWords.update(found)
        if len(violationList) == 0: return
        
        if priority == 0:
            ping = ' '
        elif priority == 1:
            ping = '<@&833185748193640478>'
        elif priority == 2:
            ping = '@here'
        elif priority == 3:
            ping = '@everyone'
        
        string = re.sub(r'(https?)(:\/\/.*?\/)', '\\1\u200B\\2', message.content)
        string = highlight(message.content, [violationDF.loc[word, 'Pattern'] for word in violationList], '[**', f'**]({message.jump_url})')
        
        alert = f'{message.author.name} {fromEvent} [a message]({message.jump_url}) in {message.channel.mention} containing: ' + ', '.join(set(containedWords))
        embed = discord.Embed(title = 'Violation: ' + ', '.join(violationList), url = message.jump_url, description = string, color = discord.Color.dark_gold())
        embed.set_author(name = message.author.name, icon_url = message.author.avatar.url)
        embed.add_field(name = '\u200b', value = alert, inline = True)
        
        if len(message.attachments) == 0:
            attachments = None
            attachmentLinks = [' ']
        elif len(message.attachments) == 1 and message.attachments[0].size < 8388608:
            attachments = await message.attachments[0].to_file()
            attachmentLinks = [' ']
        else:
            attachments = None
            attachmentLinks = [file.url for file in message.attachments]
        
        await channel.send(content = ping + '\n'.join(attachmentLinks), file = attachments, embed = embed)

    async def landmineCheck(message):
        if isinstance(message.channel, discord.Thread):
            mid = message.channel.parent_id
        else:
            mid = message.channel.id
        global landmines
        if mid not in landmines.keys():
            return
        if landmines[mid] == 0:
            return
        if mid != 825738430326636554:
            if chewtoyRole not in message.author.roles:
                return
        if random.random() >= 1/(1+np.exp(-0.075*(landmines[mid]-100))):
            await message.add_reaction("💥")
            try: await message.author.timeout(timedelta(minutes = 1.5))
            except:
                pass
            await message.channel.send(expMess(message.author))
            landmines[mid] += -1
            if landmines[mid] == 0:
                landmines.pop(mid)

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
        if message.author == bot.user or message.author.bot:
            return
        await indoctrination(message)
        await randUptumblr(message)
        await beppening(message)
        await landmineCheck(message)
        await logViolation(message)
        

    @bot.event
    async def on_raw_message_edit(payload):
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if message.author == bot.user or message.author.bot:
            return
        await beppening(message)
        await logViolation(message, 'edited')

    @bot.event
    async def on_message_edit(before, after):
        if (before.mention_everyone and not after.mention_everyone) or (len(before.role_mentions)!=0 and set(before.role_mentions)!=set(after.role_mentions)) or (len(before.mentions)!=0 and set(before.mentions)!=set(after.mentions)):
            alert = f'{before.author.name} edited [a message]({before.jump_url}) in {before.channel.mention} containing mentions'
            embed = discord.Embed(title = 'Violation: ' + 'Pings', url = before.jump_url, description = before.clean_content, color = discord.Color.dark_gold())
            embed.set_author(name = before.author.name, icon_url = before.author.avatar.url)
            embed.add_field(name = '\u200b', value = alert, inline = True)
        
            if len(before.attachments) == 0:
                attachments = None
                attachmentLinks = [' ']
            elif len(before.attachments) == 1 and before.attachments[0].size < 8388608:
                attachments = await before.attachments[0].to_file()
                attachmentLinks = [' ']
            else:
                attachments = None
                attachmentLinks = [file.url for file in before.attachments]
        
            await logChannel.send(content = ' ' + '\n'.join(attachmentLinks), file = attachments, embed = embed)

    @bot.event
    async def on_message_delete(before):
        if before.mention_everyone or ((len(before.role_mentions)!=0 or len(before.mentions)!=0) and before.type != discord.MessageType.reply) or ((len(before.role_mentions)!=0 or len(before.mentions)>1) and before.type == discord.MessageType.reply):
            alert = f'{before.author.name} deleted [a message]({before.jump_url}) in {before.channel.mention} containing mentions'
            embed = discord.Embed(title = 'Violation: ' + 'Pings', url = before.jump_url, description = before.clean_content, color = discord.Color.dark_gold())
            embed.set_author(name = before.author.name, icon_url = before.author.avatar.url)
            embed.add_field(name = '\u200b', value = alert, inline = True)
        
            if len(before.attachments) == 0:
                attachments = None
                attachmentLinks = [' ']
            elif len(before.attachments) == 1 and before.attachments[0].size < 8388608:
                attachments = await before.attachments[0].to_file()
                attachmentLinks = [' ']
            else:
                attachments = None
                attachmentLinks = [file.url for file in before.attachments]
        
            await logChannel.send(content = ' ' + '\n'.join(attachmentLinks), file = attachments, embed = embed)

    @bot.event
    async def on_raw_reaction_remove(payload):
        if not reactRemove:
            return
        user = bot.get_user(payload.user_id)
        serv = bot.get_guild(payload.guild_id)
        channel = serv.get_channel(payload.channel_id)
        emote = payload.emoji
        if user == bot.user:
            return
        else:
            msg = await channel.fetch_message(payload.message_id)
            deleteEmbed = discord.Embed(title = 'Reaction deleted', description = f'**Offender:** {user.mention}\n {str(emote)}', url = msg.jump_url, color = discord.Color.default())
            await logChannel.send(embed=deleteEmbed)

    @bot.command(name='toggleReactions', help = 'TOGGLE LOGGING OF REACTIONS')
    async def togRR(ctx):
        global reactRemove
        reactRemove = not reactRemove
        await ctx.send(f'TOGGLED LOGGING TO {reactRemove}')

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
    @bot.command(name='appeal', help = 'LODGE REQUEST TO REPEAL PUNISHMENT')
    async def appeal(ctx):
        #perm check
        userPre = ctx.author
        user = await ctds.fetch_member(userPre.id)
        punishmentRoleList = [ctds.get_role(808939025066623006), ctds.get_role(809515769665945660), ctds.get_role(1292316592226435112)]
        if not any(role in user.roles for role in punishmentRoleList):
            return
        threadChannel = ctds.get_channel(1144616583369605140)
        appealThread = await threadChannel.create_thread(name=f'Appeal Thread - {user.name}', message=None, reason='Appeal thread', invitable=False)
        await appealThread.add_user(user)
        await appealThread.send(f'{user.mention}')




    '''
    Join/Leave
        on join, dm members a copy of the rules
            add string "Randomly placed string to thwart bots! paste this into #shoelace to join" in certain spots randomly
        append user and random string added to list
        a msg from user containing string gives member role and removes them from list
        purge list every 24 hours
        on leave, immortalize their shame.
    '''

    def userKey(member):
        member = ctds.get_member(member.id)
        dt = member.joined_at
        dif = dt-serverDate
        userID = member.id
        seed = int(np.round(dif.total_seconds()))*userID
        random.seed(a=seed)
        key = random.randint(1000000, 9999999)
        return key

    @bot.event
    async def on_member_join(member):
        rulesEmbed = discord.Embed(title = 'Rules List', url = 'https://discord.com/channels/808811670327263312/808818237252304907', color = discord.Color.dark_theme())
        columns = rulesDF.columns[1:]
        rand_index = random.randint(0, len(columns)-1)
        randKey = userKey(member)
        for index in range(len(columns)):
            if rand_index == index:
                if str(rulesDF.at[1, columns[index]]) == '-----':
                    rulesEmbed.add_field(name = f'{str(columns[index])}. {str(rulesDF.at[0, columns[index]])}', value = f'To access the server, paste {str(randKey)}', inline = False)
                else:
                    rulesEmbed.add_field(name = f'{str(columns[index])}. {str(rulesDF.at[0, columns[index]])}', value = f'{str(rulesDF.at[1, columns[index]])} To access the server, paste {str(randKey)}', inline = False)
            else:
                rulesEmbed.add_field(name = str(columns[index]) + '. ' + str(rulesDF.at[0, columns[index]]), value = str(rulesDF.at[1, columns[index]]), inline = False)
        try: await member.send(f"Welcome to the Curated Tumblr Discord Server! To ensure you're not a bot, please read over the rules and paste the 7 digit key hidden in the rules into {shoelaceChannel.mention}. Upon doing so, you'll be able to access the rest of the server. Thanks, and have fun!", embed = rulesEmbed)     
        except:
            embed = discord.Embed(title = 'Oops!', description = """Looks like you don't have DMs enabled. Please enable them temporarily and use the command "1984bot, resend" to receive the rules and code to join.""", color = discord.Color.dark_theme())
            embed.set_author(name = member.name, icon_url = member.avatar.url)
            await shoelaceChannel.send(content = member.mention,embed = embed)

    @bot.command(name = 'resend', aliases = ['rS', 'resendWelcome'], help = 'REPEAT DECONTAMINATION PROCEDURES')
    async def resend(ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        await on_member_join(member)

    @bot.command(name = 'activeKeys', aliases = ['viewActiveNewMemberKeys', 'aK', 'viewKeys'] , help = 'DISPLAY NEW MATERIAL')
    @has_permissions(kick_members = True)
    async def viewKeys(ctx):
        newMemberList = []
        for member in ctds.members:
            if not ((memberRole in member.roles) or member.bot):
                newMemberList.append(member)
        pageCount = int(np.ceil(len(newMemberList)/10))
        if pageCount == 0:
            keyEmbed = discord.Embed(title = 'Active New Member Keys:', description = 'None', color = discord.Color.greyple())
            await ctx.send(embed = keyEmbed)
        elif pageCount == 1:
            keyEmbed = discord.Embed(title = 'Active New Member Keys:', description = ' ', color = discord.Color.greyple())
            for member in newMemberList:
                keyEmbed.add_field(name = member.name, value = str(userKey(member)), inline = False)
            await ctx.send(embed = keyEmbed)
        else:
            for i in range(pageCount):
                keyEmbed = discord.Embed(title = 'Active New Member Keys:', description = f'Page {i+1} of {pageCount}', color = discord.Color.greyple())
                if 10*(i+1) >= len(newMemberList):
                    for member in newMemberList[10*i:]:
                        keyEmbed.add_field(name = member.name, value = str(userKey(member)), inline = False)
                    await ctx.send(embed = keyEmbed)
                else:
                    for member in newMemberList[10*i:10*(i+1)]:
                        keyEmbed.add_field(name = member.name, value = str(userKey(member)), inline = False)
                    await ctx.send(embed = keyEmbed)

    @bot.event
    async def on_member_remove(member):
        leaveEmbed = discord.Embed(title = 'Goodbye!', description = f'{member.mention} has left with the following roles: {member.roles}', color = discord.Color.greyple())
        leaveEmbed.set_author(name = member.name, icon_url = member.avatar.url)
        await logChannel.send(embed = leaveEmbed)

    '''
    Reaction Roles
    lol no idea how this works
    '''

    @bot.event
    async def on_member_update(before, member):
        if member == bot.user:
            if not (member.guild.me.nick == nick or member.guild.me.nick == None):
                await member.guild.me.edit(nick = nick)

    @bot.command(name = 'nick', aliases = ['nickname', 'nN', 'changenick', 'chnick'], help = 'REINDEX SUBJECT')
    async def chnick(ctx, member: discord.Member = bot.user, *nickname):
        global nick
        newNick = ' '.join(nickname)
        if member == bot.user: nick = newNick
        await member.edit(nick = newNick)

    @bot.command(name = 'ping', help = 'MONITOR CONNECTION')
    async def ping(ctx):
        await ctx.send(f'Ping is {str(np.round(1000*bot.latency, 2))} ms')

    @bot.command(name = 'pingAverage', aliases = ['pA', 'pingAvg'], help = 'ACCOUNT FOR VARIATIONS IN CONNECTION')
    @has_permissions(kick_members = True)
    async def pingAvg(ctx):
        async with ctx.typing():
            start = time.perf_counter()
            pings = []
            while len(pings)<20:
                ping = 1000*bot.latency
                if (ping not in pings):
                    pings.append(ping)
                time.sleep(2)
        await ctx.send(f'Average ping over {str(np.round(time.perf_counter()-start))} is {str(np.round(np.mean(pings), 2))} ms')

    @bot.command(name = 'reload', aliases = ['f5', 'refresh'], help = 'RELOAD')
    @has_permissions(kick_members = True)
    async def reload(ctx):
        print('\nRELOADING ..........................\n')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    @bot.command(name = 'disconnect', aliases = ['dc', 'logoff'], help = 'DEACTIVATE')
    @has_permissions(kick_members = True)
    async def disconnect(ctx):
        rulesDF.to_csv(rulesFilePath, sep = ';')
        blacklistDF.to_csv(blacklistFilePath, sep = ';')
        await bot.close()

    '''
    ANALYSIS PACKAGE
    '''

    @bot.command(name = 'search', aliases = ['searchTerm'], help = 'QUANTIFY USAGE OF TERM')
    @has_permissions(kick_members = True)
    async def search(ctx, *terms):
        async with ctx.typing():
            searchTerm = ' '.join(terms)
            totalUsage = 0
            messageCount = 0
            timer = 0
            authorList = {}
            occurenceList = {}
            #print('ENGAGED')
            for channel in ctds.text_channels:
                #print('SEARCHING ' + channel.name)
                start = time.perf_counter()
                history = await channel.history(limit=None).flatten()
                timer += time.perf_counter()-start
                messageCount += len(history)
                for message in history:
                    num = len(re.findall(searchTerm, message.content, flags=re.I))
                    if num > 0:
                        #print('FOUND MESSAGE WITH ' + str(num) + ' ENTRIES')
                        totalUsage += num
                        if message.author.id in authorList:
                            authorList[message.author.id] += 1
                            occurenceList[message.author.id] += num
                        else:
                            authorList[message.author.id] = 1
                            occurenceList[message.author.id] = num
            entry = max(authorList, key=authorList.get)
            leadingUser = bot.get_user(int(entry))
            searchEmbed = discord.Embed(title = f'Results for {searchTerm}:', description = f'{totalUsage} occurences with {len(authorList)} users among {messageCount} messages', color = discord.Color.dark_gold())
            searchEmbed.add_field(name = f'Leading user of {searchTerm}: {leadingUser.mention}', value = '​', inline = False)
            searchEmbed.add_field(name = f"Number of {leadingUser.name}'s messages containing {searchTerm}", value = f'{authorList[entry]}', inline = True)
            searchEmbed.add_field(name = f"Number of {leadingUser.name}'s uses of {searchTerm}", value = f'{occurenceList[entry]}', inline = True)
            print(f'MESSAGES EXTRACTED OVER {timer} SECONDS')
        await ctx.send(embed=searchEmbed)

    @bot.command(name = 'timestamp', aliases = ['time', 'giveTime'], help = 'GENERATE UBIQUITOUS TIMESTAMP')
    async def timestamp(ctx, *time):
        foundTime = dateparser.parse(" ".join(time))
        try: # tTdDfFR
            await ctx.send(f'''
    `<t:{int(foundTime.timestamp())}:t>`   <t:{int(foundTime.timestamp())}:t>
    `<t:{int(foundTime.timestamp())}:T>`   <t:{int(foundTime.timestamp())}:T>
    `<t:{int(foundTime.timestamp())}:d>`   <t:{int(foundTime.timestamp())}:d>
    `<t:{int(foundTime.timestamp())}:D>`   <t:{int(foundTime.timestamp())}:D>
    `<t:{int(foundTime.timestamp())}:f>`   <t:{int(foundTime.timestamp())}:f>
    `<t:{int(foundTime.timestamp())}:F>`   <t:{int(foundTime.timestamp())}:F>
    `<t:{int(foundTime.timestamp())}:R>`   <t:{int(foundTime.timestamp())}:R>
            ''')
        except AttributeError:
            await ctx.send('`NO TIME DISCOVERED WITHIN PARAMETERS`' , allowed_mentions = discord.AllowedMentions(replied_user = True), reference = ctx.message)

    @bot.command(name = 'pingMeAnything', aliases = ['pma'], help = 'SEND A PINGING MESSAGE TO THOSE WHO DESIRE IT')
    async def pma(ctx, *content):
        auth = ctx.author
        bannedFromAPMA = ctds.get_role(1292316592226435112)
        if bannedFromAPMA not in auth.roles:
            if auth.id not in recentIDsPMA:
                mainBody = '<@&1086001388091363328>'
                msg = ' '.join(content)
                embed = discord.Embed(title = 'Ping Me Anything Message:', description = msg, color = discord.Color.orange())
                embed.set_author(name = auth.name, icon_url = auth.avatar.url)
                await ctx.channel.send(mainBody, embed=embed)
                await ctx.message.delete()
                recentIDsPMA[auth.id] = 0
                await asyncio.sleep(3600)
                recentIDsPMA.pop(auth.id) 

    @bot.command(name = 'askMeAnything', aliases = ['ama'], help = 'ASK A PINGING QUESTION TO THOSE WHO DESIRE IT')
    async def ama(ctx, *content):
        auth = ctx.author
        bannedFromAPMA = ctds.get_role(1292316592226435112)
        if bannedFromAPMA not in auth.roles:
            if auth.id not in recentIDsAMA:
                mainBody = '<@&839403091119964180>'
                msg = ' '.join(content)
                embed = discord.Embed(title = 'Ask Me Anything Question:', description = msg, color = discord.Color.orange())
                embed.set_author(name = auth.name, icon_url = auth.avatar.url)
                await ctx.channel.send(mainBody, embed=embed)
                await ctx.message.delete()
                recentIDsAMA[auth.id] = 0
                await asyncio.sleep(3600)
                recentIDsAMA.pop(auth.id)            

    @bot.command(name = 'landmine', help = 'PLANT A LANDMINE IN THE SPECIFIED CHANNEL')
    async def landmine(ctx, channel: discord.abc.GuildChannel = None):
        if isinstance(channel, discord.Thread): channel = channel.parent
        if not (isinstance(channel, discord.TextChannel) or isinstance(channel, discord.ForumChannel)) and channel != None:
            await ctx.channel.send(f"Unable to landmine {channel.mention}!")
            return
        if ctx.channel == landmineChannel:
            if ctx.author.id not in recentIDsLandmine:
                recentIDsLandmine[ctx.author.id] = 0
            if recentIDsLandmine[ctx.author.id] == 6:
                await ctx.channel.send(f"{ctx.author.mention} needs to wait for resupply before laying more mines!")
            else:
                if channel == None:
                    channel = ctds.get_channel(random.choice(validLandmineChannels))
                if channel.id in validLandmineChannels:
                    recentIDsLandmine[ctx.author.id] += 1
                    localVal = recentIDsLandmine[ctx.author.id]
                    global landmines
                    if channel.id not in landmines.keys():
                        landmines[channel.id] = 1
                    else:
                        landmines[channel.id] += 1
                    await ctx.send(f"Planted a landmine in {channel.mention}!")
                    await asyncio.sleep(300)
                    if recentIDsLandmine[ctx.author.id] >= localVal:
                        recentIDsLandmine[ctx.author.id] = 0
                    
                else:
                    await ctx.channel.send(f"Interserver treaties have outlawed the planting of landmines in {channel.mention}. For shame, you would-be war criminal.")
        else:
            msg = await ctx.send(f"Go to {landmineChannel.mention} to plant landmines.")
            await asyncio.sleep(3)
            await msg.delete()
        
    @bot.command(name = 'viewLandmines', aliases = ['vL', 'minesweeper'], help = 'VIEW ACTIVE MINEFIELDS')
    async def viewLandmines(ctx):
        if ctx.channel == landmineChannel:
            lCount = 0
            cCount = 0
            for x, y in landmines.items():
                lCount += y
                cCount += 1
            if len(landmines.keys()) <= 20:
                mineEmbed = discord.Embed(title = f'Minesweep results:', description = f'Detected {lCount} mines across {cCount} channels!', color = discord.Color.dark_gold())
                for i in range(int((len(landmines.items())-(len(landmines.items())%2))/2)):
                    mineEmbed.add_field(name = f"{ctds.get_channel(list(landmines.keys())[2*i]).mention} : {landmines[list(landmines.keys())[2*i]]}", value = f"{ctds.get_channel(list(landmines.keys())[2*i+1]).mention} : {landmines[list(landmines.keys())[2*i+1]]}", inline = True)
                if len(landmines.items())%2 == 1:
                    mineEmbed.add_field(name = f"{ctds.get_channel(list(landmines.keys())[-1]).mention} : {landmines[list(landmines.keys())[-1]]}", value = f" ", inline = True)
                await ctx.channel.send(embed = mineEmbed)
        else:
            msg = await ctx.send(f"Go to {landmineChannel.mention} to check for landmines.")
            await asyncio.sleep(3)
            await msg.delete()

    @bot.command(name = 'proliferateMines', aliases = ['pM', 'massmine'], help = 'LAY A NUMBER OF MINES IN A CHANNEL')
    @has_permissions(kick_members = True)
    async def massmine(ctx, channel: discord.abc.GuildChannel = None, num: int = 1):
        if isinstance(channel, discord.Thread): channel = channel.parent
        if not (isinstance(channel, discord.TextChannel) or isinstance(channel, discord.ForumChannel)) and channel != None:
            await ctx.channel.send(f"Unable to landmine {channel.mention}!")
            return
        if channel == None:
            channel = ctds.get_channel(random.choice(validLandmineChannels))
        if channel.id not in landmines.keys():
            if num <= 0:
                await ctx.send(f"Cannot remove landmines from a channel without any!")
                return
            landmines[channel.id] = num
        else:
            if (landmines[channel.id] + num) <= 0:
                landmines.pop(channel.id)
                await ctx.send(f"Removed all landmines from {channel.mention}.")
            landmines[channel.id] += num
        if num >= 0:
            await ctx.send(f"Planted {num} landmines in {channel.mention}!")
        else:
            await ctx.send(f"Removed {np.abs(num)} landmines from {channel.mention}")

    await bot.add_cog(Music(bot))

    return bot

bot = asyncio.run(mainBot())
bot.run(token)
