import queue
import threading

import MySQLdb
from MySQLdb.cursors import DictCursor

from otter.conf import settings


def get_db_conn():
    conn = MySQLdb.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        db=settings.DB_NAME,
        user=settings.DB_USER,
        passwd=settings.DB_PASS,
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    return conn


class MySQLConnection:

    def __init__(self, raw_conn, pool):
        self.conn = raw_conn
        self.pool = pool
        self.in_use = True

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

    def begin(self):
        return self.conn.begin()

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        if self.in_use:  # 防止重复归还
            self.pool.release(self)
            self.in_use = False

    def is_usable(self):
        try:
            self.conn.ping(True)
            return True
        except (Exception,):
            return False

    def real_close(self):
        try:
            self.conn.close()
        except (Exception,):
            pass


class MySQLPool:

    def __init__(self, maxsize=10):
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.pool = queue.Queue(maxsize)
        self.used = set()  # 已借出的连接对象
        self.total = 0  # 当前连接总数

    def create_new_conn(self):
        raw_conn = get_db_conn()
        conn_obj = MySQLConnection(raw_conn, self)
        return conn_obj

    def connection(self):
        try:
            conn = self.pool.get(block=False)
            if not conn.is_usable():  # 不可用
                conn.real_close()  # 关闭
                with self.lock:
                    self.total -= 1
                    assert self.total >= 0, 'total should never be negative'
                    if self.total < self.maxsize:
                        conn = self.create_new_conn()
                        self.total += 1
                    else:
                        raise Exception('All connections are in use')
        except queue.Empty:
            with self.lock:
                if self.total < self.maxsize:
                    conn = self.create_new_conn()
                    self.total += 1
                else:
                    raise Exception('All connections are in use')
        with self.lock:
            self.used.add(conn)
        conn.in_use = True
        return conn

    def release(self, conn):
        with self.lock:
            if conn in self.used:
                self.used.remove(conn)
            else:
                return
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            conn.real_close()
            with self.lock:
                self.total -= 1
                assert self.total >= 0, 'total should never be negative'

    def close_all(self):
        with self.lock:
            while not self.pool.empty():
                conn = self.pool.get_nowait()
                conn.real_close()
                self.total -= 1
                assert self.total >= 0, 'total should never be negative'
            for conn in list(self.used):
                conn.real_close()
                self.used.remove(conn)
                self.total -= 1
                assert self.total >= 0, 'total should never be negative'


db_pool = MySQLPool()


def create_dbpool_conn():
    conn = db_pool.connection()  # 从连接池中获取一个连接
    return conn
