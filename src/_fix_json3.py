import json, re

path = 'd:/Project/paper/代码/HYGMA/results/sacred/12/info.json'
with open(path, 'r') as f:
    text = f.read()

# Try fixing by truncating the last incomplete list entry
# The error is at line 8107 - the last line is incomplete
# Remove trailing incomplete data until valid

lines = text.split('\n')
# Remove trailing empty/whitespace lines
while lines and not lines[-1].strip():
    lines.pop()
# Remove trailing comma on last non-empty line
if lines and lines[-1].rstrip().endswith(','):
    lines[-1] = lines[-1].rstrip()[:-1]

# Rebuild
text2 = '\n'.join(lines)
# Close open structures
open_braces = text2.count('{') - text2.count('}')
open_brackets = text2.count('[') - text2.count(']')
text2 += '\n' + '}' * open_braces + ']' * open_brackets

try:
    data = json.loads(text2)
    print(f"Fixed! {len(data)} keys")
    with open(path, 'w') as f:
        json.dump(data, f)
    print("Saved.")
except Exception as e:
    print(f"Still broken: {e}")
    # Try removing last line entirely
    if len(lines) > 1:
        lines.pop()
        text3 = '\n'.join(lines)
        ob = text3.count('{') - text3.count('}')
        obr = text3.count('[') - text3.count(']')
        text3 += '\n' + '}' * ob + ']' * obr
        try:
            data = json.loads(text3)
            print(f"Fixed by removing last line! {len(data)} keys")
            with open(path, 'w') as f:
                json.dump(data, f)
            print("Saved.")
        except Exception as e2:
            print(f"Still broken after removing line: {e2}")
