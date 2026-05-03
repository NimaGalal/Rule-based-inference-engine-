from parsing import parse_rules, parse_facts


def check_condition(cond,facts):
    attr = cond['attribute']
    val  = cond['value']
    typ  = cond['type']

    if typ == 'boolean':
        return facts.get(attr) == True

    if typ == 'is':
        return facts.get(attr) == val

    if typ == 'equals':
        return facts.get(attr) == val

    if typ == 'lt':
        fact_val = facts.get(attr)
        if fact_val is None:
            return False
        return fact_val < val

    if typ == 'gt':
        fact_val = facts.get(attr)
        if fact_val is None:
            return False
        return fact_val > val

    return False


def rule_fires(rule, facts):
    conditions = rule['conditions']
    connective = rule['connective']

    if connective == 'OR':
        return any(check_condition(c, facts) for c in conditions)
    else:
        return all(check_condition(c, facts) for c in conditions)


def conclusion_already_known(conclusion, facts):
    attr = conclusion['attribute']
    val  = conclusion['value']
    typ  = conclusion['type']

    if typ == 'boolean':
        return facts.get(attr) == True
    elif typ in ('is', 'equals'):
        return facts.get(attr) == val
    return False


def apply_conclusion(conclusion,facts):
    attr = conclusion['attribute']
    val  = conclusion['value']
    typ  = conclusion['type']

    if typ == 'boolean':
        facts[attr] = True
    elif typ in ('is','equals'):
        facts[attr] = val


def forward_chaining(rules,facts):
    print(" Forward Chaining")
    print(f"Initial facts: {facts}\n")

    cycle = 1
    while True:
        new_facts_added = {}

        for rule in rules:
            conclusion = rule['conclusion']
            if rule_fires(rule, facts) and not conclusion_already_known(conclusion, facts):
                attr = conclusion['attribute']
                val  = conclusion['value'] if conclusion['type'] != 'boolean' else True
                new_facts_added[attr] = val

        if not new_facts_added:
            print(f"Cycle {cycle}: No new facts derived. Forward chaining complete.")
            break

        facts.update(new_facts_added)
        print(f"Cycle {cycle} New facts added: {new_facts_added}")
        print(f"All facts: {facts}\n")
        cycle += 1

    return facts


rules       = parse_rules('rules.txt')
facts, goal = parse_facts('facts.txt')

forward_chaining(rules, facts)
