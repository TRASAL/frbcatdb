import unittest
from pyfrbcatdb import dbase as dbase

class BasicDBTest(unittest.TestCase):
    def setUp(self):
        self.connection, self.cursor = dbase.connectToDB(dbHost='localhost',
                                            dbName='frbcat_test',
                                            userName='travis_pymysql',
                                            dbPassword='password')
    def tearDown(self):
        self.connection.close()

    def test_select_all_frbs(self):
        n = self.cursor.execute('SELECT * from frbs')
        self.assertEqual(3, n)

if __name__ == '__main__':
    unittest.main()
