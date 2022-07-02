import json
import os


class CacheException(Exception):
    pass


class FileBackedCache(object):

    LOCAL_FILE_NAME = '.small-improvements-cache'

    def is_setup(self):
        return os.path.isfile(self.LOCAL_FILE)

    @property
    def LOCAL_FILE(self):
        return os.environ['HOME'] + f'/{self.LOCAL_FILE_NAME}'

    def read_data(self):
        try:
            with open(self.LOCAL_FILE, 'rb') as data_file:
                return json.loads(data_file.read())
        except IOError:
            raise CacheException(
                'Could not find {}. You should run setup first.'.format(self.LOCAL_FILE)
            )
        except json.decoder.JSONDecodeError:
            raise CacheException(
                'File {} was not valid JSON. You should re-run setup to fix.'.format(
                    self.LOCAL_FILE
                )
            )
        except Exception:
            raise CacheException(
                'Cound not read {}. You should re-run setup to fix.'.format(
                    self.LOCAL_FILE
                )
            )

    def write_data(self, data):
        try:
            with open(self.LOCAL_FILE, 'w') as data_file:
                data = json.dumps(data, sort_keys=True, indent=4)
                data_file.write(data)
        except IOError:
            raise CacheException('Could not write {}'.format(self.LOCAL_FILE))


class MemoryBackedCache(object):
    def is_setup(self):
        return bool(getattr(self, '_cache', {}))

    def read_data(self):
        data = getattr(self, '_cache', {})
        if not data:
            raise CacheException('No data found')
        return data

    def write_data(self, data):
        self._cache = data
