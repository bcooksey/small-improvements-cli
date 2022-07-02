from datetime import datetime

import constants


class MockSIClient(object):
    def __init__(self, *args, **kwargs):
        self._meetings = []
        self._last_talking_point = {}
        self._last_note = {}

    def _set_meetings(self, meetings):
        for meeting in meetings:
            if isinstance(meeting['calendarDate'], datetime):
                meeting['calendarDate'] = self._format_date(meeting['calendarDate'])
        self._meetings = meetings

    def get_me(self):
        return {
            'id': '2LThXtNqTuO7EgEN35jwWA',
            'isManager': True,
            'manager': {
                'firstName': 'Alex',
                'id': '4PRgWtMqDtO7FgEN35jtKL',
                'name': 'Alex Apricot',
            },
        }

    def get_team(self, manager_id):
        return [
            {
                'firstName': 'Alice',
                'id': '123SsBCllZGRQ2wwxeosRvYfA',
                'name': 'Alice Appleton',
                'isActive': True,
            },
            {
                'firstName': 'Robert',
                'id': 'i8naB-eiS4WsjqozAL5j7w',
                'name': 'Robert Rogers',
                'isActive': True,
            },
        ]

    def create_meeting(self, owner_id, teammate_id, meeting_date, status='SHARED'):
        is_draft = False if status == 'SHARED' else True
        return {
            'id': 123,
            'calendarDate': self._format_date(meeting_date),
            'participants': [],
            'isDraft': is_draft,
        }

    def get_meetings_with_teammate(self, teammate_id, start_date=None, end_date=None):
        if start_date:
            meetings = []
            for meeting in self._meetings:
                if (
                    datetime.strptime(meeting['calendarDate'], constants.DATE_FORMAT)
                    >= start_date
                ):
                    meetings.append(meeting)
            return meetings

        return self._meetings

    def share_meeting(self, meeting_id):
        pass

    def add_talking_point(self, meeting_id, content, **talking_point_options):
        self._last_talking_point = {
            'args': [meeting_id, content],
            'kwargs': talking_point_options,
        }

    def add_note(self, meeting_id, content, **note_options):
        self._last_note = {
            'args': [meeting_id, content],
            'kwargs': note_options,
        }

    def set_base_url(self, base_url=None):
        pass

    def _check_for_401(self, response, **kwargs):
        pass

    def _format_date(self, date):
        return date.strftime(constants.DATE_FORMAT)
