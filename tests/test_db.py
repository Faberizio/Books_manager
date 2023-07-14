import unittest
from src.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = Database()

    # We want to test for singleton
    def test_singleton(self):
        conn1 = Database()
        conn2 = Database()

        self.assertEqual(conn1, conn2)

    def test_postgres_version(self):
        # We want to test database connectivity
        pg_version = "PostgreSQL 12.13"
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT version();")  # execute sql statement
            db_version = cursor.fetchone()[0]  # get one row
            self.assertTrue(db_version.startswith(pg_version))
            # self.assertRegex(db_version, r"^(PostgreSQL 12.13)")

    def tearDown(self) -> None:
        self.conn.close()
