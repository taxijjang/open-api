import logging

from django.conf import settings

debug_string = "\x1b[33m{text}\x1b[0m"


def DEBUG(*args):
    try:
        text = ' '.join([str(x) for x in args])
        if settings.DEBUG:
            logging.log(logging.DEBUG, debug_string.format(text=text))
        else:
            logging.log(logging.DEBUG, text)
    except Exception:
        pass

class StorageDB(object):
    def __init__(self, con):
        self.con = con
        self._execute_count = 0  # commit, rollback을 했는지 확인하기 위한 counter

    def cursor(self):
        return Cursor(self, self.con.cursor())

    def commit(self):
        self.con.commit()
        self._execute_count = 0
        DEBUG("COMMIT;")

    def rollback(self):
        self.con.rollback()
        self._execute_count = 0
        DEBUG("ROLLBACK;")


class Cursor:
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    @property
    def description(self):
        return self.cursor.description

    @property
    def _executed(self):
        return self.cursor._executed

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def execute(self, *args, **kwargs):
        r = self.cursor.execute(*args, **kwargs)
        DEBUG(self.cursor._executed)
        self.connection._execute_count += 1
        return r

    def fetchone(self, with_keys=False):
        _fetchone = self.cursor.fetchone()
        if with_keys:
            if _fetchone:
                fields = [x[0] for x in self.description]
                return {k: v for k, v in zip(fields, _fetchone)}
            else:
                return None
        else:
            return _fetchone

    def fetchall(self, with_keys=False):
        _fetchall = self.cursor.fetchall()
        if with_keys:
            if _fetchall:
                fields = [x[0] for x in self.description]
                return [{k: v for k, v in zip(fields, item)} for item in _fetchall]
            else:
                return []
        else:
            return _fetchall