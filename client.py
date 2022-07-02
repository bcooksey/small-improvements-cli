import json

import click
import requests

import constants


class SIClient(object):

    BASE_URL = None
    API_URL = None

    def __init__(self, token, base_url=None):
        self.session = requests.Session()
        self.session.headers.update(
            {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        )
        self.session.hooks['response'].append(self._check_for_401)
        self.set_base_url(base_url)

    def get_me(self):
        response = self.session.get(f'{self.API_URL}/users/me')
        response.raise_for_status()
        return response.json()

    def get_team(self, manager_id):
        team_response = self.session.get(
            f'{self.API_URL}/users/medium', params={'managerId': manager_id}
        )
        team_response.raise_for_status()
        return team_response.json()

    def create_meeting(self, owner_id, teammate_id, meeting_date, status='SHARED'):
        is_draft = False if status == 'SHARED' else True
        response = self.session.post(
            f'{self.API_URL}/meetings',
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            data=json.dumps(
                {
                    'participants': [{'id': owner_id}, {'id': teammate_id}],
                    'date': self._format_date(meeting_date) + 'T00:00:00z',
                    'isDraft': is_draft,
                }
            ),
        )
        response.raise_for_status()
        return response.json()

    def get_meetings_with_teammate(self, teammate_id, start_date=None, end_date=None):
        params = {'participants': teammate_id}
        if start_date:
            params['startDate'] = self._format_date(start_date)
        if end_date:
            params['endDate'] = self._format_date(end_date)
        response = self.session.get(
            f'{self.API_URL}/meetings', params=params
        )
        response.raise_for_status()
        return response.json()

    def share_meeting(self, meeting_id):
        response = self.session.patch(
            f"{self.API_URL}/meetings/{meeting_id}",
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            data=json.dumps({'status': 'SHARED'}),
        )
        response.raise_for_status()

    def add_talking_point(self, meeting_id, content, visibility='SHARED'):
        talking_point = {
            'meetingId': meeting_id,
            'content': content,
            'visibility': visibility,
        }

        response = self.session.post(
            f'{self.API_URL}/meetings/{meeting_id}/talkingpoints',
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            data=json.dumps([talking_point]),
        )
        response.raise_for_status()

    def add_note(self, meeting_id, content, visibility='SHARED'):
        note = {'meetingId': meeting_id, 'content': content, 'visibility': visibility}

        response = self.session.post(
            f'{self.API_URL}/meetings/{meeting_id}/notes',
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            data=json.dumps(note),
        )
        response.raise_for_status()

    def set_base_url(self, base_url=None):
        self.BASE_URL = base_url or constants.DEFAULT_BASE_URL
        self.API_URL = self.BASE_URL + '/api/v2'

    def _check_for_401(self, response, **kwargs):
        if response.status_code == 401:
            click.echo(f'Invalid SI_TOKEN. Please visit {self.BASE_URL}/app/personal-access-tokens to generate a token. Then run `export SI_TOKEN=<your_token>`')
            raise click.Abort()

    def _format_date(self, date):
        return date.strftime(constants.DATE_FORMAT)
