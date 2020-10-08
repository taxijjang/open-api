from lib.libTools import cached_property


class MemStatus:
    def __init__(self, cursor, memstatus):
        self.cur = cursor
        self.memstatus = memstatus

    @cached_property
    def data(self):
        sql = "SELECT " \
              "`login`," \
              "`trade`" \
              "FROM `mem_status_func` WHERE `memstatus`=%s;"
        self.cur.execute(sql, (self.memstatus,))
        return self.cur.fetchone(with_keys=True)

    @property
    def login(self):
        return self.data['login']

    @property
    def trade(self):
        return self.data['trade']
