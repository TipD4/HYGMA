import json

path = 'd:/Project/paper/代码/HYGMA/results/sacred/12/info.json'
with open(path, 'r') as f:
    text = f.read()

# Find the last complete entry and truncate
# The corrupt part is at line 8107, char 81943
# Try to truncate to last valid JSON
pos = text.rfind(']}')
if pos > 0:
    # Check if we can close it properly
    fixed = text[:pos+2]
    # Need to close any open structures
    # Count braces
    open_braces = fixed.count('{') - fixed.count('}')
    open_brackets = fixed.count('[') - fixed.count(']')
    fixed += '}' * open_braces + ']' * open_brackets
    try:
        data = json.loads(fixed)
        # Save fixed version
        with open(path, 'w') as f:
            json.dump(data, f)
        print(f"Fixed! Saved {len(data)} keys")
    except Exception as e:
        print(f"Still broken: {e}")
else:
    print("No safe truncation point found")
