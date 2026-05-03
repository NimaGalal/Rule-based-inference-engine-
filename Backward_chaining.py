# Check if the goal is satisfied

def is_in_facts(theGoal, theFacts):
    if theGoal in theFacts and theFacts[theGoal] is True:
        return True

    for attribute, value in theFacts.items():
        if value == theGoal:
            return True

    return False

# Cheks if the condition is true

def condition_is_true(condition, facts):

    cond_type = condition['type']
    attribute = condition['attribute']
    value = condition.get('value')

    if cond_type == 'is':
        return attribute in facts and facts[attribute] == value

    elif cond_type == 'boolean':
        return facts.get(attribute) is True

    elif cond_type == 'equals':
        return attribute in facts and facts[attribute] == value

    elif cond_type == 'lt':
        return attribute in facts and facts[attribute] < value

    elif cond_type == 'gt':
        return attribute in facts and facts[attribute] > value

    return False

def rule_prove(goal, rules):

    matching_rules = []

    for rule in rules:
        conclusion = rule['conclusion']

        if conclusion['type'] == 'boolean' and conclusion['attribute'] == goal:
            matching_rules.append(rule)

        elif conclusion['type'] == 'is' and conclusion['value'] == goal:
            matching_rules.append(rule)

    return matching_rules


def extracting_facts(condition):

    cond_type = condition['type']

    if cond_type == 'is':
        return condition['value']

    elif cond_type == 'boolean':
        return condition['attribute']

    elif cond_type == 'equals':
        return f"{condition['attribute']} = {condition['value']}"

    elif cond_type == 'lt':
        return f"{condition['attribute']} < {condition['value']}"

    elif cond_type == 'gt':
        return f"{condition['attribute']} > {condition['value']}"

    return None

def backward_chain_trace(goal, facts, rules, visited=None, depth=0):

    if visited is None:
        visited = set()

    indent = "  " * depth

    print(f"{indent} Proving: {goal}")

    # Check if goal is already a known fact
    if is_in_facts(goal, facts):
        print(f"{indent} '{goal}' is already a known fact!")
        return True

    # Prevent infinite loops
    if goal in visited:
        print(f"{indent} '{goal}' already trying - loop detected")
        return False

    # Mark this goal as being tried
    visited.add(goal)

    # Find rules that can prove this goal
    candidate_rules = rule_prove(goal, rules)

    if not candidate_rules:
        print(f"{indent} No rules can prove '{goal}'")
        return False

    print(f"{indent} Found {len(candidate_rules)} rule(s)")

    # Try each candidate rule
    for rule in candidate_rules:
        print(f"{indent} Trying Rule {rule['id']}: {rule['raw']}")

        if rule['connective'] == 'AND':
            all_ok = True

            for condition in rule['conditions']:
                cond_type = condition['type']

                # Handle numeric comparisons directly
                if cond_type in ['lt', 'gt', 'equals']:
                    print(f"{indent} Checking: {extracting_facts(condition)}")
                    if condition_is_true(condition, facts):
                        print(f"{indent} Condition satisfied")
                    else:
                        print(f"{indent} Condition failed")
                        all_ok = False
                        break

                # Handle 'is' and 'boolean' by recursion
                else:
                    subgoal = extracting_facts(condition)
                    print(f"{indent} Need to prove: {subgoal}")

                    if backward_chain_trace(subgoal, facts, rules, visited, depth + 1):
                        print(f"{indent} Subgoal '{subgoal}' proved")
                        # Check if this is a newly proved fact
                        if not is_in_facts(subgoal, facts):
                            print(f"{indent} NEW FACT: {subgoal}")
                    else:
                        print(f"{indent} Subgoal '{subgoal}' failed")
                        all_ok = False
                        break

            if all_ok:
                print(f"{indent} Rule {rule['id']} SUCCEEDS! '{goal}' is proved")
                if not is_in_facts(goal, facts):
                    print(f"{indent} NEW FACT PROVED: {goal}")
                return True
            else:
                print(f"{indent} Rule {rule['id']} fails")

        elif rule['connective'] == 'OR':
            for condition in rule['conditions']:
                cond_type = condition['type']

                if cond_type in ['lt', 'gt', 'equals']:
                    print(f"{indent} Checking OR: {extracting_facts(condition)}")
                    if condition_is_true(condition, facts):
                        print(f"{indent} Condition satisfied")
                        print(f"{indent} Rule {rule['id']} SUCCEEDS! '{goal}' is proved")
                        if not is_in_facts(goal, facts):
                            print(f"{indent} NEW FACT PROVED: {goal}")
                        return True
                    else:
                        print(f"{indent} Condition failed")
                        continue

                else:
                    subgoal = extracting_facts(condition)
                    print(f"{indent} Trying OR: {subgoal}")

                    if backward_chain_trace(subgoal, facts, rules, visited, depth + 1):
                        print(f"{indent} OR condition '{subgoal}' succeeded")
                        print(f"{indent} Rule {rule['id']} SUCCEEDS! '{goal}' is proved")
                        if not is_in_facts(goal, facts):
                            print(f"{indent} NEW FACT PROVED: {goal}")
                        return True

            print(f"{indent} Rule {rule['id']} fails (no OR condition met)")

    print(f"{indent} Cannot prove '{goal}'")
    return False


backward_chain_trace(goal, facts, rules)

pprint(rules)

print(facts)
