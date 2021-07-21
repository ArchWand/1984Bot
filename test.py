import pandas as pd
import re

string = '''
The word piss is in this sentence, along with pissed, pissing, and empis​​​​​​​soning, and, worst of all, pi5️⃣5️⃣.'''
string = string[1:]
violationDF = pd.DataFrame.from_dict({"Violation": ["piss"], "Priority": [0], "Pattern": [r"\b\w*?piss.*?\b"]})
violationDF.set_index(violationDF.columns[0], inplace = True)

def parseContent(message):
    string = message.lower()
    # All below replaces characters in a string (common substitutions) to prevent people from escaping the blacklist
    replaceDict = {
        '[\u200B-\u200F\u2028-\u2029\uFEFF]': '', # Zero-width characters
        '5': 's',
        '[^\x20-\x7F]': ''
    }

    for replaceFrom, replaceTo in replaceDict.items():
        string = re.sub(replaceFrom, replaceTo, string)
    return string
content = parseContent(string)

def telemetry(*args):
    for arg in args:
        print(arg)

violationList = []
containedWords = set()
for row in violationDF.itertuples():
    found = re.findall(row[2], content)
    if found:
        containedWords.update(found)
        violationList.append(row[1])

iHighlight = {}

for word in violationList:
    pattern = violationDF.iloc[word, 1]
    prev = False
    for i in range(len(string)):
        # telemetry()
        match = re.match(pattern, parseContent(string[i:]))
        if match:
            if not prev:
                tgtLen = match.end() - match.start()
                iHighlight[i] = len(string)
                parseLen = len(parseContent(string[i:iHighlight[i]]))
                while tgtLen != parseLen:
                    iHighlight[i] = iHighlight[i] - 1
                    parseLen = len(parseContent(string[i:iHighlight[i]]))
                
            prev = True
            continue
        prev = False

def results():
    global string
    print(string)
    
    offset = 0
    for key in iHighlight:
        # telemetry(' ', string, (key, iHighlight[key]), offset)
        # toAdd = "_"*(iHighlight[key] - key)
        toAdd = f'[{string[key + offset:iHighlight[key] + offset]}]' # (https://www.youtube.com/watch?v=dQw4w9WgXcQ)'
        string = string[:key + offset] + toAdd + string[iHighlight[key] + offset:]
        offset += len(toAdd) + key - iHighlight[key]
    
    print(string)
    print(iHighlight)
    print()

results()
