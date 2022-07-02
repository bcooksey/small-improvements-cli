import unittest
from datetime import datetime, timedelta

from constants import DATE_FORMAT
from small_improvements import MemorySmallImprovements
from tests.mock_client import MockSIClient


class TestSmallImprovements(unittest.TestCase):
    def setUp(self):
        self.si = MemorySmallImprovements('fake_token')
        self.si.client = MockSIClient()
        self.si.setup('fake-domain')

    def test_sync_team(self):
        # From a fresh start, should load in data
        self.si.sync_team(overwrite=False)
        raw_data = self.si.read_data()
        self.assertGreater(len(raw_data), 0)

        # If we add on to existing data, resync shouldn't destroy it
        raw_data['me']['some_crazy_key'] = 'some_value'
        self.si.write_data(raw_data)
        self.si.sync_team(overwrite=False)
        raw_data = self.si.read_data()
        self.assertIn('some_crazy_key', raw_data['me'])

        # If we say overwrite, then we should pull fresh from client
        self.si.sync_team(overwrite=True)
        raw_data = self.si.read_data()
        self.assertNotIn('some_crazy_key', raw_data['me'])

    def test_get_me(self):
        self.assertIn('id', self.si.get_me())

    def test_get_manager(self):
        self.assertIn('id', self.si.get_manager())

    def test_get_team(self):
        self.assertEqual(2, len(self.si.get_team()))

    def test_get_manager_and_team(self):
        team = self.si.get_manager_and_team()
        # Manager should come first (not out of importance, but because
        # from UX standpoint memorizing #1 is manager is easier)
        self.assertEqual('manager', team[0]['relationship'])

    def test_add_nickname(self):
        team = self.si.get_team()
        self.si.add_nickname(team['Alice Appleton'], 'Ali')

        team = self.si.get_team()
        self.assertEqual('Ali', team['Alice Appleton'].get('nickname'))

    def test_find_or_create_meeting(self):
        alice = self.si.get_team()['Alice Appleton']

        # Without any meetings, should create one for tomorrow
        now = datetime.now()
        meeting = self.si.find_or_create_meeting(alice['id'])
        self.assertIn('id', meeting)
        tomorrow = now + timedelta(days=1)
        self.assertEqual(
            meeting['calendarDate'],
            tomorrow.strftime(DATE_FORMAT),
            'Meeting was not for tomorrow',
        )

        # If we call it again, should get the upcoming meeting back
        self.si.client._set_meetings([meeting])
        self.assertEqual(meeting, self.si.find_or_create_meeting(alice['id']))

        # If we have an old meeting to go off of, should create the new one 7 days from then
        meeting['calendarDate'] = now - timedelta(days=3)
        self.si.client._set_meetings([meeting])
        meeting = self.si.find_or_create_meeting(alice['id'])
        expected_date = now + timedelta(days=4)
        self.assertEqual(
            meeting['calendarDate'],
            expected_date.strftime(DATE_FORMAT),
            'Meeting was not 7 days in future',
        )

    def test_find_upcoming_meeting(self):
        teammate = self.si.get_team()['Alice Appleton']
        now = datetime.now()

        # First up, what happens where there are no meetings
        self.assertEqual(None, self.si.find_upcoming_meeting(teammate['id']))

        # And if there are meetings but they are in the past
        meetings = [{'id': 123, 'calendarDate': now - timedelta(days=1)}]
        self.si.client._set_meetings(meetings)
        self.assertEqual(None, self.si.find_upcoming_meeting(teammate['id']))

        # And now one in the future
        meetings.append({'id': 456, 'calendarDate': now + timedelta(days=1)})
        self.si.client._set_meetings(meetings)
        self.assertEqual(meetings[1], self.si.find_upcoming_meeting(teammate['id']))

    def test_get_meeting_url(self):
        url = self.si.get_meeting_url({'id': 'abc123'})
        self.assertEqual('https://www.small-improvements.com/app/meeting/abc123', url)

    def test_add_talking_point(self):
        self.si.add_talking_point(123, 'test', talking_point_options={'is_private': True})

        self.assertEqual(self.si.client._last_talking_point['kwargs']['visibility'], 'PRIVATE')

    def test_add_note(self):
        self.si.add_note(123, 'test', note_options={'is_private': True})

        self.assertEqual(self.si.client._last_note['kwargs']['visibility'], 'PRIVATE')
