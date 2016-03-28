import re

# Finds pairs like 'item = "WScri",' or 'permission = -135782688;'
ASSIGN_RE = re.compile(r'(\w+) = ("[^"]+"|.\d+)')
# Finds a word inserted in the middle, the ([^\w]) make sure it's not part of
# another word. I know this is really ugly.
MAGIC2 = r'([^\w])({})([^\w])'


# Find the variables

var_cont = open("vars.js").read()
replacements = {}
for found in ASSIGN_RE.finditer(var_cont):
    name, value = found.groups()
    replacements[name] = value


# Replace them in the code

# Replace the middle word but keep the start and ending. This is a workaround 
# for my inability to write proper regex
def replace(match):
    return match.group(1) + replacements[match.group(2)] + match.group(3)

code = open("code.js").read()
code_new_f = open("code_new.js", "w")
code_new = code
for name, value in replacements.items():
    # Replace all the variables with their values
    code_new = re.sub(MAGIC2.format(name), replace, code_new)
# Remove unnecessare string joins like '"Wscrip" + "t"'
code_new = code_new.replace('" + "', '')
code_new_f.write(code_new)
code_new_f.close()
