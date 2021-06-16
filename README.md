# 1984bot  
Custom server bot for the [CuratedTumblr Discord Server](https://discord.gg/aWtJjSFG5X), a discord server for the [r/CuratedTumblr](https://www.reddit.com/r/CuratedTumblr) subreddit

## Functions:
- Word Highlight (Maybe find some way to fit into other blacklist too)
- Cone/Kick/Ban message
- Reaction Roles / Role Commands
- Add/Remove blacklist
- Join/Leave message

## Blacklist structure
Message containing blacklist
File containing blacklist and keywords `[class, topic, 'clarification', [keywords]]`
	On initialization, all keywords added to a list.
Add command: classification, topic, clarification, keywords
Remove command: class and index/topic
Edit command: class, topic, revision field 1, etc
	Revision field can be skipped with `^` character.
View command: class, topic; returns keywords

## Rules structure
Message containing rules
Add command: 'rule'(, reindex number)
Remove command: index
Edit command: index, 'rule'

## Word Highlight
```py
for keyword in blacklist:
	if msgcontent.contains(keyword):
		violationList.append(keyword)
```
send message in mod channel "message (copy) violates these keywords: [violationList]"

## Cone/Ice
log cone/ice update
If being added, send message in mod channel "hey! user just got coned/iced! length and reason?"
Upon reply, post reason and punishment in #rulebreaker-central
Set timer for length, automatically remove cone/ice at end
	length can be omitted with `^` character

## Kick/ban
log kick/ban
send mod channel msg "hey! user got kicked/banned! reason?"
dm user with reason

Join/Leave
on join, dm members a copy of the rules
	add string "Randomly placed string to thwart bots! paste this into #shoelace to join" in certain spots randomly
append user and random string added to list
a msg from user containing string gives member role and removes them from list
purge list every 24 hours
on leave, immortalize their shame.

Reaction Roles
https://discordpy.readthedocs.io/en/latest/api.html#discord.on_raw_reaction_add
