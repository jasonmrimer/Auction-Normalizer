import unittest
import sqlite3
import os
from multiprocessing import context


class ConstraintTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.remove('test_db')
        self.conn = sqlite3.connect('test_db')
        self.cursor = self.conn.cursor()
        file = open('../src/create.sql')
        sql = file.read()
        file.close()

        self.cursor.executescript(sql)

    def tearDown(self) -> None:
        self.conn.close()

    def test_query_1_number_of_users(self):
        file = open('../src/query1.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            13422,
            users[0][0]
        )

    def test_query_2_users_from_new_york(self):
        conn = sqlite3.connect('test_db')
        cursor = conn.cursor()
        file = open('../src/query2.sql')
        sql = file.read()
        file.close()
        users = cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            80,
            users[0][0]
        )


if __name__ == '__main__':
    unittest.main()
