import unittest

from utils import match_choices_to_teammates


class TestUtils(unittest.TestCase):
    def generate_team(self):
        return [{'name': 'Alice'}, {'name': 'Bob'}, {'name': 'Charlie'}]

    def test_match_choices_to_teammates(self):
        team = self.generate_team()

        found, missing = match_choices_to_teammates('Alice', team)
        self.assertEqual(found[0], team[0])

        found, missing = match_choices_to_teammates('Alice,Bob', team)
        self.assertEqual(2, len(found))

        # Extra spaces shouldn't matter
        found, missing = match_choices_to_teammates(' Alice , Bob ', team)
        self.assertEqual(2, len(found))

        # Casing shouldn't matter
        found, missing = match_choices_to_teammates('alice', team)
        self.assertEqual(1, len(found))

        # Misses should be tracked
        found, missing = match_choices_to_teammates('Sue', team)
        self.assertEqual(0, len(found))
        self.assertEqual(['Sue'], missing)

        # Mix of matches and misses
        found, missing = match_choices_to_teammates('Alice,Sue', team)
        self.assertEqual(1, len(found))
        self.assertEqual(1, len(missing))

    def test_match_choices_to_teammates_prefers_nicknames(self):
        team = self.generate_team()

        # Simple case where teammate has a nickname
        team[1]['nickname'] = 'Bob'
        team[1]['name'] = 'Robert'

        found, missing = match_choices_to_teammates('Bob', team)
        self.assertEqual(found[0], team[1])

        # Nickname and full name match, teammate with nickname comes first
        team[2]['name'] = 'Bob the Second'

        found, missing = match_choices_to_teammates('Bob', team)
        self.assertEqual(found[0], team[1])

        # Nickname and full name match, teammate with full name comes first
        team[0]['name'] = 'Bob the First'

        found, missing = match_choices_to_teammates('Bob', team)
        self.assertEqual(found[0], team[1])

    def test_match_choices_to_teammates_handles_indexes(self):
        team = self.generate_team()

        # UI is 1-based, so 1 should be first teammate
        found, missing = match_choices_to_teammates('1', team)
        self.assertEqual(1, len(found))
        self.assertEqual(found[0], team[0])

        found, missing = match_choices_to_teammates('1,3', team)
        self.assertEqual(2, len(found))

        # Invalid indexes should be a miss
        found, missing = match_choices_to_teammates('99', team)
        self.assertEqual(0, len(found))
        self.assertEqual(['99'], missing)

        # Mix of names and indexes is ok
        found, missing = match_choices_to_teammates('Alice,2', team)
        self.assertEqual(2, len(found))

    def test_match_choices_to_teammates_handles_all_option(self):
        team = self.generate_team()

        found, missing = match_choices_to_teammates('all', team)
        self.assertEqual(3, len(found))
        self.assertEqual(0, len(missing))

        # `all` gets ignored if anything else is with it
        found, missing = match_choices_to_teammates('all,Alice', team)
        self.assertEqual(1, len(found))

    def test_match_choices_to_teammates_handles_team_option(self):
        team = self.generate_team()
        team[0]['relationship'] = 'manager'
        team[1]['relationship'] = 'report'
        team[2]['relationship'] = 'report'

        found, missing = match_choices_to_teammates('team', team)
        self.assertEqual(2, len(found))
        self.assertNotIn(team[0], found)
        self.assertEqual(0, len(missing))

        found, missing = match_choices_to_teammates('all,Alice', team)
        self.assertEqual(1, len(found))

    def test_match_choices_to_teammates_handles_manager_option(self):
        team = self.generate_team()
        team[0]['relationship'] = 'manager'
        team[1]['relationship'] = 'report'
        team[2]['relationship'] = 'report'

        found, missing = match_choices_to_teammates('manager', team)
        self.assertEqual(1, len(found))

        found, missing = match_choices_to_teammates('all,Alice', team)
        self.assertEqual(1, len(found))

    def test_match_choices_to_teammates_handles_list(self):
        team = self.generate_team()

        found, missing = match_choices_to_teammates(['Alice'], team)
        self.assertEqual(1, len(found))
