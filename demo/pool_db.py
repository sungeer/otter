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
        self.in_use = True  # 防止重复归还

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

    def begin(self):
        return self.conn.begin()

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        self.pool.release(self)

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

    def __init__(self):
        self.lock = threading.Lock()
        self.pool = queue.Queue(5)  # 最多5个空闲连接
        self.used = set()  # 已借出的连接对象

    def create_new_conn(self):
        raw_conn = get_db_conn()
        conn_obj = MySQLConnection(raw_conn, self)
        return conn_obj

    def connection(self):
        try:
            conn = self.pool.get(block=False)
            if not conn.is_usable():  # 不可用
                conn.real_close()  # 关闭
                conn = self.create_new_conn()
        except queue.Empty:
            conn = self.create_new_conn()
        with self.lock:
            self.used.add(conn)
        conn.in_use = True
        return conn

    def release(self, conn):
        if conn.in_use is False:  # 防止重复释放
            return
        conn.in_use = False
        with self.lock:
            self.used.remove(conn)
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            conn.real_close()

    def close_all(self):
        with self.lock:
            while not self.pool.empty():
                conn = self.pool.get_nowait()
                conn.real_close()
            for conn in list(self.used):
                conn.real_close()
                self.used.remove(conn)


db_pool = MySQLPool()


def create_dbpool_conn():
    conn = db_pool.connection()  # 从连接池中获取一个连接
    return conn
