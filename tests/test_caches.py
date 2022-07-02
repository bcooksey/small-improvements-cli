import os
import unittest

from caches import FileBackedCache, CacheException


class TestableFileBackedCache(FileBackedCache):
    @property
    def LOCAL_FILE(self):
        return os.getcwd() + '/tests/files/example-team'


class MissingFileBackedCache(FileBackedCache):
    @property
    def LOCAL_FILE(self):
        return os.getcwd() + '/tests/files/does-not-exist'


class TestCaches(unittest.TestCase):
    def test_file_cache(self):
        cache = TestableFileBackedCache()

        self.assertTrue(cache.is_setup())
        self.assertTrue(cache.read_data())

    def test_file_cache_missing_file(self):
        cache = MissingFileBackedCache()
        with self.assertRaises(CacheException):
            cache.read_data()
