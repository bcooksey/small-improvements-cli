import os

import click

import constants
from small_improvements import SmallImprovements
from utils import match_choices_to_teammates

si = SmallImprovements(os.environ.get('SI_TOKEN'))

COMMAND_ALIASES = {'an': 'add-note', 'ap': 'add-talking-point', 'sm': 'share-meeting'}


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        if cmd_name in COMMAND_ALIASES:
            return click.Group.get_command(self, ctx, COMMAND_ALIASES[cmd_name])
        ctx.fail(f'Unknown Command: {cmd_name}')


def prompt_teammate_selection(message, team):
    if len(team) == 1:
        # Only one option, default to it (likely manager)
        return [team[0]], []

    click.echo(message)
    print_team(team)
    selection = click.prompt('Selection (ex. `alice`, `1,2,5`, `team`, `1,2,alice`)')

    return match_choices_to_teammates(selection, team)


def confirm_teammate_selection(prefix, found_teammates):
    found_names = map(lambda x: x.get('nickname') or x['firstName'], found_teammates)
    click.confirm(
        f'{prefix} {", ".join(found_names)}',
        default=True,
        abort=True,
        show_default=True,
    )


def process_or_prompt_teammate_selection(desired_teammates, team, prompt):
    found_teammates = []

    if desired_teammates:
        # Specified folks right in line
        found_teammates, missing_teammates = match_choices_to_teammates(
            list(desired_teammates), team
        )
    else:
        found_teammates, missing_teammates = prompt_teammate_selection(prompt, team)

    if missing_teammates:
        raise click.BadParameter(
            f'"{", ".join(missing_teammates)}" did not match anybody on your team'
        )

    return found_teammates


def print_team(team):
    if not team:
        raise click.BadParameter(f'Could not load team')

    is_manager_first = team[0]['relationship'] == 'manager'
    for index, teammate in enumerate(team):
        if index == 0:
            if is_manager_first:
                click.echo(f'=== Manager ===')
            else:
                click.echo(f'=== Team ===')
        nickname = f"({teammate['nickname']})" if teammate.get('nickname') else ''
        click.echo(f"{index + 1}. {teammate['name']} {nickname}")
        if index == 0 and is_manager_first and len(team) > 1:
            click.echo(f'\n=== Team ===')


@click.group(cls=AliasedGroup)
def cli():
    pass


@cli.command(name='setup')
def setup():
    '''
    Initial command to run to get setup. Can re-run if your system gets messed up.
    '''
    if si.is_setup():
        click.confirm(
            f'Already setup. Do you want to overwrite?',
            default=False,
            abort=True,
            show_default=True,
        )

    subdomain = click.prompt(
        'What subdomain do you use to access Small Improvements?', default=constants.DEFAULT_SUBDOMAIN
    )
    si.setup(subdomain)
    click.echo(f'Setup Complete')


@cli.command(name='list-team')
def list_team():
    '''
    Dumps the cached list of your teammates
    '''
    print_team(si.get_manager_and_team())


@cli.command(name='sync-team')
def sync_team():
    '''
    Re-syncs your team from SI, adding any new teammates that are found.
    '''
    si.sync_team()


@cli.command(name='add-nickname')
def add_nickname():
    '''
    Adds a nickname to a teammate
    '''

    team = si.get_manager_and_team()
    found_teammates, missing_teammates = prompt_teammate_selection(
        'Who do you want to add a nickname too?', team
    )

    if missing_teammates:
        raise click.BadParameter(
            f'"{", ".join(missing_teammates)}" did not match anybody on your team'
        )

    nickname = click.prompt('Nickname')

    confirm_teammate_selection('Add nickname to', found_teammates)

    si.add_nickname(found_teammates[0], nickname)


@cli.command(name='add-talking-point')
@click.option('is_private', '--private', '-p', is_flag=True, default=False)
@click.option(
    'is_draft_meeting',
    '--draft-meeting',
    '-dm',
    is_flag=True,
    default=False,
    help='When creating a meeting, should it default to draft?',
)
@click.option('desired_teammates', '--teammate', '-t', multiple=True)
@click.argument('content', nargs=-1)
def add_talking_point(
    content, desired_teammates, is_draft_meeting, **talking_point_options
):
    '''
    (Alias ap) Adds a talking point to one or more meetings. If there is not
    an upcoming meeting with a teammate, one will be created. Any meetings
    created default to 7 days since last meeting (or tomorrow if there are no
    past meetings)

    Examples:

    # Add a talking point using interactive prompts

    small-improvements ap

    # Add a talking point to meeting with Alice

    small-improvements ap -t Alice Update on Project

    # Add a private talking point to a meeting

    small-improvements ap -p Bonus this year is $XXXX

    # Add a talking point to meetings with Alice and Bob
    small-improvements ap -t Alice -t Bob New Review Process
    '''

    if content:
        content = ' '.join(content)
        click.echo(f'Talking Point: {content}')
    else:
        content = click.prompt('Talking Point')

    team = si.get_manager_and_team()

    chosen_teammates = process_or_prompt_teammate_selection(
        desired_teammates, team, 'Who do you want to add the talking point to?'
    )

    confirm_teammate_selection('Add this talking point to', chosen_teammates)

    for teammate in chosen_teammates:
        meeting = si.find_or_create_meeting(teammate['id'], is_draft=is_draft_meeting)
        si.add_talking_point(
            meeting['id'], content, talking_point_options=talking_point_options
        )


@cli.command(name='share-meeting')
@click.option('desired_teammates', '--teammate', '-t', multiple=True)
def share_meeting(desired_teammates):
    '''
    (Alias sm) Shares the upcoming meeting with a teammate (so they can see the talking points)
    '''

    team = si.get_manager_and_team()

    chosen_teammates = process_or_prompt_teammate_selection(
        desired_teammates, team, 'Who do you want to share the meeting with?'
    )

    confirm_teammate_selection('Share meeting(s) with', chosen_teammates)

    for teammate in chosen_teammates:
        next_meeting = si.find_upcoming_meeting(teammate['id'])
        if next_meeting:
            si.share_meeting(next_meeting['id'])
        else:
            click.echo(f"No upcoming meeting found for {teammate['name']}")


@cli.command(name='view-meeting')
def view_meeting():
    '''
    View an upcoming meeting
    '''

    team = si.get_manager_and_team()

    found_teammates, missing_teammates = prompt_teammate_selection(
        'Which meeting do you want to view?', team
    )

    if missing_teammates:
        raise click.BadParameter(
            f'"{", ".join(missing_teammates)}" did not match anybody on your team'
        )

    if len(found_teammates) > 1:
        raise click.BadParameter('You should only select one teammate')

    teammate = found_teammates[0]
    name = teammate.get('nickname', teammate['firstName'])

    meeting = si.find_upcoming_meeting(teammate['id'])
    if not meeting:
        click.echo(f'You do not have an upcoming meeting with {name}')
        return

    click.echo(f"Meeting Link: {si.get_meeting_url(meeting)}")


@cli.command(name='add-note')
@click.option('is_private', '--private', '-p', is_flag=True, default=False)
@click.option(
    'is_draft_meeting',
    '--draft-meeting',
    '-dm',
    is_flag=True,
    default=False,
    help='When creating a meeting, should it default to draft?',
)
@click.option('desired_teammates', '--teammate', '-t', multiple=True)
@click.argument('content', nargs=-1)
def add_note(content, desired_teammates, is_draft_meeting, **note_options):
    '''
    (Alias an) Adds a note to one or more meetings. If there is not
    an upcoming meeting with a teammate, one will be created. Any meetings
    created default to 7 days since last meeting (or tomorrow if there are no
    past meetings)
    '''
    if content:
        content = ' '.join(content)
    else:
        content = click.edit()
        if not content:
            raise click.BadParameter('Must provide a note body')

    click.echo(f'Note: {content}')

    team = si.get_manager_and_team()

    chosen_teammates = process_or_prompt_teammate_selection(
        desired_teammates, team, 'Who do you want to add the note to?'
    )

    confirm_teammate_selection('Add this note to', chosen_teammates)

    for teammate in chosen_teammates:
        meeting = si.find_or_create_meeting(teammate['id'], is_draft=is_draft_meeting)
        si.add_note(meeting['id'], content, note_options=note_options)


if __name__ == '__main__':
    cli()
