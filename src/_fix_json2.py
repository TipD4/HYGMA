path = 'd:/Project/paper/代码/HYGMA/results/sacred/12/info.json'
with open(path, 'r') as f:
    text = f.read()

# The file ends with an incomplete list entry. Let's try appending closing brackets.
# Sacred info.json is a flat dict: {key: [objects], key_T: [ints], ...}
# We need to close any open arrays/objects at the end.

# Try progressively more closing brackets
import re

# Remove trailing comma/newline then close
text = text.rstrip()
while text.endswith(','):
    text = text[:-1]

# Count open vs close
open_braces = text.count('{') - text.count('}')
open_brackets = text.count('[') - text.count(']')

print(f"Open braces: {open_braces}, Open brackets: {open_brackets}")
text += '}' * open_braces + ']' * open_brackets

import json
try:
    data = json.loads(text)
    print(f"Fixed! {len(data)} keys")
    with open(path + '.fixed', 'w') as f:
        json.dump(data, f)
except Exception as e:
    print(f"Failed: {e}")
    # Try harsher fix: remove the last incomplete array and close properly
    # Find last complete '[' ...
