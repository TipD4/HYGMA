import re, json

path = 'd:/Project/paper/代码/HYGMA/results/sacred/12/info.json'
with open(path, 'r') as f:
    text = f.read()

# Sacred info.json is a flat dict: {"key": [...], "key_T": [...], ...}
# Extract all complete key-value pairs using regex
# Each key is a string, value is a list

# Find all complete "[...]" arrays and their preceding keys
# Pattern: "key": [ ... complete list ... ]

# Simpler approach: find the last position where we have a valid partial parse
# Try truncating at increasing positions backwards

lines = text.split('\n')
for trim_lines in range(0, min(100, len(lines))):
    truncated = '\n'.join(lines[:len(lines)-trim_lines])
    # Remove trailing comma
    truncated = truncated.rstrip()
    if truncated.endswith(','):
        truncated = truncated[:-1]
    # Close open structures
    ob = truncated.count('{') - truncated.count('}')
    obr = truncated.count('[') - truncated.count(']')
    truncated += '\n' + '}' * ob + ']' * obr
    try:
        data = json.loads(truncated)
        print(f"Fixed by trimming {trim_lines} lines! {len(data)} keys")
        # Check we have the important keys
        for k in ['test_return_mean', 'test_battle_won_mean']:
            if k in data:
                print(f"  {k}: {len(data[k])} points, last={data[k][-1]}")
        with open(path, 'w') as f:
            json.dump(data, f)
        print("Saved.")
        break
    except:
        continue
else:
    print("Could not fix by trimming up to 100 lines")
