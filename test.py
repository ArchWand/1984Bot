from timeit import timeit
import re

def parseStringLoop(string):
    string = string.lower()
    # All below replaces characters in a string (common substitutions) to prevent people from escaping the blacklist
    replaceDict = {
        '\u200B': '', # Zero-width characters
        '1': 'i',
        '3': 'e',
        '4': 'a',
        '5': 's',
        'ñ': 'n',
        '7': 't',
        '0': 'o',
        '8': 'b',
        '&': 'and',
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
        r'\n': ' '
    }
    
    out = ''
    for letter in string:
        if letter in replaceDict:
            letter = replaceDict[letter]
        out += letter
    return re.sub('[^\x20-\x7F]', '', out)

def parseRegexLoop(string):
    string = string.lower()
    # All below replaces characters in a string (common substitutions) to prevent people from escaping the blacklist
    replaceDict = {
        '[\u200B-\u200F\u2028-\u2029\uFEFF]': '', # Zero-width characters
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
        r'\bur': 'your',
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
        r'\n': ' ',
        '[^\x20-\x7F]': ''
    }

    for replaceFrom, replaceTo in replaceDict.items():
        string = re.sub(replaceFrom, replaceTo, string)
    return string

testString = "\U0001f1fc\U0001f170\u271d\u262a\u2653 \u2b55\u26ce\u2626 for \U0001f1f9\U0001f1ed3 5\u26514\U0001f1f03️⃣!" + r"T​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​h​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​i​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​s​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​s​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​t​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​r​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​i​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​n​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​g​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​i​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​s​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​n​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​o​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​w​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​m​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​u​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​c​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​h​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​ ​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​l​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​o​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​n​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​g​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​e​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​r​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​."*0

reptCount = 20000

strLpTime = timeit(lambda: parseStringLoop(testString), number = reptCount)
regexTime = timeit(lambda: parseRegexLoop(testString), number = reptCount)

print(f'\nTest string of length {len(testString)}, ran {reptCount} times\n')

print(f'Regex: {regexTime} s, {regexTime / reptCount * 1000} ms per run')
print(f'Output: {parseRegexLoop(testString)}\n')

print(f'StrLp: {strLpTime} s, {strLpTime / reptCount * 1000} ms per run')
print(f'Output: {parseStringLoop(testString)}\n')
