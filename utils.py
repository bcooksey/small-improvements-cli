import re


def match_name_to_teammates(name, team):
    found_teammate = None
    for teammate in team:
        if name.lower() == teammate.get('nickname', '').lower():
            return teammate
        elif name.lower() in teammate['name'].lower():
            found_teammate = teammate

    return found_teammate


def match_choice_to_teammate(choice, team):
    choice = choice.strip()
    match = re.match('(\d+)$', choice)
    if match:
        # We got an index
        index = int(match.group(0)) - 1
        if index < len(team):
            return team[index]
    else:
        # Assume it's a name
        found = match_name_to_teammates(choice, team)
        if found:
            return found

    return None


def match_choices_to_teammates(choices, team):
    found_teammates = []
    missing_teammates = []

    if isinstance(choices, str):
        if choices.lower() == 'all':
            found_teammates = team
        elif choices.lower() == 'team':
            for teammate in team:
                if teammate['relationship'] == 'report':
                    found_teammates.append(teammate)
        elif choices.lower() == 'manager':
            for teammate in team:
                if teammate['relationship'] == 'manager':
                    found_teammates.append(teammate)
                    break
        elif ',' in choices:
            choices = choices.split(',')
        else:
            choices = [choices]

    if found_teammates:
        return found_teammates, missing_teammates

    for choice in choices:
        found_teammate = match_choice_to_teammate(choice, team)
        if found_teammate:
            found_teammates.append(found_teammate)
        else:
            missing_teammates.append(choice)

    return found_teammates, missing_teammates
