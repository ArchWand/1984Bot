import discord
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('discordToken')

client = discord.Client()

blacklistKeywords = ['test']



@client.event
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

'''
Rules structure
    Message containing rules
    Add command: 'rule'(, reindex number)
    Remove command: index
    Edit command: index, 'rule'
'''

'''
Word Highlight
    for keyword in blacklist:
        if msgcontent.contains(keyword):
            violationList.append(keyword)
    send message in mod channel "message (copy) violates these keywords: [violationList]"
'''




@client.event
async def on_message(message):
    if message.author == client.user:
        return
    violationList = []
    logChannel = client.get_channel(851191799464984646)
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

client.run(token)


    
