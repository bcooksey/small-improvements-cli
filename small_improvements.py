from datetime import datetime, timedelta

import constants
from caches import FileBackedCache, MemoryBackedCache
from client import SIClient


class BaseSmallImprovements(object):
    def __init__(self, token):
        base_url = None

        try:
            base_url = self.get_base_url()
        except:
            pass

        self.client = SIClient(token, base_url=base_url)

    def setup(self, subdomain):
        self.client.set_base_url(constants.BASE_URL_TEMPLATE.format(subdomain))
        self.sync_team(overwrite=True)

    def sync_team(self, overwrite=False):
        me = self.client.get_me()

        fresh_team = self.client.get_team(me['id'])

        if overwrite:
            data = {}
        else:
            try:
                data = self.read_data()
            except:
                # No eixsting data, start fresh
                data = {}

        data['me'] = data.get('me', {})
        data['me'].update({'id': me['id'], 'isManager': bool(me.get('reports', []))})
        data['baseUrl'] = me.get('company', {}).get('baseUrl', '')

        data['manager'] = data.get('manager', {})
        data['manager'].update(
            {
                'id': me['manager']['id'],
                'firstName': me['manager']['firstName'],
                'name': me['manager']['name'],
                'relationship': 'manager',
            }
        )

        team = data.get('team', {})
        for teammate in fresh_team:
            if not teammate['isActive']:
                continue

            teammate = {k: teammate[k] for k in ['firstName', 'name', 'id']}
            teammate['relationship'] = 'report'
            found = False
            for key, existing_teammate in team.items():
                if teammate['id'] == existing_teammate['id']:
                    existing_teammate.update(teammate)
                    found = True
                    break

            if not found:
                team[teammate['name']] = teammate

        data['team'] = team
        self.write_data(data)

    def get_base_url(self):
        data = self.read_data()
        return data.get('baseUrl') or constants.DEFAULT_BASE_URL

    def get_me(self):
        data = self.read_data()
        return data.get('me')

    def get_manager_and_team(self):
        return [self.get_manager()] + list(self.get_team().values())

    def get_manager(self):
        data = self.read_data()
        return data.get('manager')

    def get_team(self):
        data = self.read_data()
        return data.get('team')

    def add_nickname(self, teammate, nickname):
        data = self.read_data()

        for key, existing_teammate in data['team'].items():
            if teammate['id'] == existing_teammate['id']:
                data['team'][key]['nickname'] = nickname
                break

        self.write_data(data)

    def find_or_create_meeting(self, teammate_id, is_draft=False):
        '''
        Finds the upcoming meeting, or creates it if it doesn't exist

        Can set is_draft to start meeting as a draft (unshared)
        '''
        next_meeting = self.find_upcoming_meeting(teammate_id)
        if not next_meeting:
            now = datetime.now()
            last_week = now - timedelta(
                days=8
            )  # 8 days to be safe with any TZ math SI may do
            meetings = self.client.get_meetings_with_teammate(
                teammate_id, start_date=last_week
            )
            if meetings:
                # Assume meeting should occur 7 days since last one
                last_meeting_date = datetime.strptime(
                    meetings[0]['calendarDate'], constants.DATE_FORMAT
                )
                meeting_date = last_meeting_date + timedelta(days=7)
            else:
                # Never had a meeting with this teammate, so default to tomorrow
                meeting_date = now + timedelta(days=1)

            me = self.get_me()
            status = 'DRAFT' if is_draft else 'SHARED'
            next_meeting = self.client.create_meeting(
                me['id'], teammate_id, meeting_date, status=status
            )

        return next_meeting

    def find_upcoming_meeting(self, teammate_id):
        """
        Finds the first (most imminent) for a particular teammate
        """
        next_meeting = None

        now = datetime.now()
        meetings = self.client.get_meetings_with_teammate(teammate_id, start_date=now)
        if meetings:
            next_meeting = meetings[0]

        return next_meeting

    def get_meeting_url(self, meeting):
        base_url = self.get_base_url()
        return f"{base_url}/app/meeting/{meeting['id']}"

    def add_talking_point(self, meeting_id, content, talking_point_options=None):
        content = self._convert_text_to_markup(content)
        visibility = 'SHARED'
        if talking_point_options:
            if talking_point_options.get('is_private'):
                visibility = 'PRIVATE'

        self.client.add_talking_point(meeting_id, content, visibility=visibility)

    def share_meeting(self, meeting_id):
        self.client.share_meeting(meeting_id)

    def add_note(self, meeting_id, content, note_options=None):
        content = self._convert_text_to_markup(content)

        visibility = 'SHARED'
        if note_options:
            if note_options.get('is_private'):
               visibility = 'PRIVATE'

        self.client.add_note(meeting_id, content, visibility=visibility)

    def _convert_text_to_markup(self, text):
        return ''.join(map(lambda x: f'<p>{x}</p>', text.split('\n')))


class SmallImprovements(BaseSmallImprovements, FileBackedCache):
    pass


class MemorySmallImprovements(BaseSmallImprovements, MemoryBackedCache):
    pass
