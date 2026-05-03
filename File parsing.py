import re
from pprint import pprint

def parse_condition(text):
    """
    Parse a single condition or conclusion string into a dict.

    Supported patterns:
        'attr is value'   -> {'type': 'is',      'attribute': ..., 'value': ...}
        'attr = number'   -> {'type': 'equals',  'attribute': ..., 'value': float}
        'attr < number'   -> {'type': 'lt',      'attribute': ..., 'value': float}
        'attr > number'   -> {'type': 'gt',      'attribute': ..., 'value': float}
        'bare_word'       -> {'type': 'boolean', 'attribute': ..., 'value': None}
    """
    text = text.strip()

    m = re.fullmatch(r'([\w\s]+?)\s+is\s+([\w]+)', text)
    if m:
        return {'type': 'is', 'attribute': m.group(1).strip(), 'value': m.group(2).strip()}

    m = re.fullmatch(r'([\w]+)\s*=\s*([\w.]+)', text)
    if m:
        raw = m.group(2)
        val = float(raw) if re.match(r'^-?\d+(\.\d+)?$', raw) else raw
        return {'type': 'equals', 'attribute': m.group(1).strip(), 'value': val}

    m = re.fullmatch(r'([\w]+)\s*<\s*([\d.]+)', text)
    if m:
        return {'type': 'lt', 'attribute': m.group(1).strip(), 'value': float(m.group(2))}

    m = re.fullmatch(r'([\w]+)\s*>\s*([\d.]+)', text)
    if m:
        return {'type': 'gt', 'attribute': m.group(1).strip(), 'value': float(m.group(2))}

    if re.fullmatch(r'[\w_]+', text):
        return {'type': 'boolean', 'attribute': text, 'value': None}

    raise ValueError(f"Unrecognised condition: '{text}'")


def parse_rules(filepath):
    """
    Read and parse rules.txt.

    Each rule becomes a dict:
    {
        'id'         : int,           # rule number (1-indexed)
        'raw'        : str,           # original line
        'connective' : 'AND' | 'OR',  # how conditions are joined
        'conditions' : [list of condition dicts],
        'conclusion' : conclusion dict
    }
    """
    rules = []

    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    for idx, line in enumerate(lines, start=1):
        if ' THEN ' not in line:
            continue

        if_part, then_part = line.split(' THEN ', 1)
        if_part = re.sub(r'^IF\s+', '', if_part, flags=re.IGNORECASE).strip()

        if ' OR ' in if_part:
            connective = 'OR'
            raw_conds  = [c.strip() for c in if_part.split(' OR ')]
        else:
            connective = 'AND'
            raw_conds  = [c.strip() for c in if_part.split(' AND ')]

        rules.append({
            'id'         : idx,
            'raw'        : line,
            'connective' : connective,
            'conditions' : [parse_condition(c) for c in raw_conds],
            'conclusion' : parse_condition(then_part.strip())
        })

    return rules



def parse_facts(filepath):
    """
    Read and parse facts.txt.

    Returns (facts_dict, goal):
        facts_dict : { attribute -> value }
                     'attr is value'  ->  facts['attr']  = 'value'  (str)
                     'attr = number'  ->  facts['attr']  = number   (float)
                     bare word        ->  facts['word']  = True
        goal       : str | None  (from a line starting with #goal)
    """
    facts = {}
    goal  = None

    with open(filepath, 'r') as f:
        raw_text = f.read()

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Extract goal directive: #goal prove <fact>
        if line.lower().startswith('#goal'):
            m = re.search(r'#goal\s+prove\s+([\w_]+)', line, re.IGNORECASE)
            if m:
                goal = m.group(1).strip()
            continue

        line = line.split('#')[0].strip()  # strip inline comments
        if not line:
            continue

        tokens = line.split()
        i = 0
        while i < len(tokens):
            tok = tokens[i]

            # 'attr is value'
            if i + 2 < len(tokens) and tokens[i + 1] == 'is':
                facts[tok] = tokens[i + 2]
                i += 3
                continue

            # 'attr = value' (separate tokens)
            if i + 2 < len(tokens) and tokens[i + 1] == '=':
                raw = tokens[i + 2]
                facts[tok] = float(raw) if re.match(r'^-?\d+(\.\d+)?$', raw) else raw
                i += 3
                continue

            # 'attr=value' (joined token)
            m = re.fullmatch(r'([\w]+)=([\w.]+)', tok)
            if m:
                raw = m.group(2)
                facts[m.group(1)] = float(raw) if re.match(r'^-?\d+(\.\d+)?$', raw) else raw
                i += 1
                continue

            # bare boolean fact
            if re.fullmatch(r'[\w_]+', tok):
                facts[tok] = True
                i += 1
                continue

            i += 1

    return facts, goal


rules       = parse_rules('rules.txt')
facts, goal = parse_facts('facts.txt')

print(f"Loaded {len(rules)} rules and {len(facts)} facts.")
if goal:
    print(f"Goal: '{goal}'")

print("\n--- RULES ---")
for r in rules:
    print(f"\nRule {r['id']}: {r['raw']}")
    print(f"  connective : {r['connective']}")
    print(f"  conditions : {r['conditions']}")
    print(f"  conclusion : {r['conclusion']}")

print("\n--- FACTS ---")
pprint(facts)
print("\nGoal:", goal)
