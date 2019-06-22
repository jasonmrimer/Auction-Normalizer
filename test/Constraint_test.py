import csv
import sqlite3
import unittest


# insert users ./
# insert bids ./
# insert auctions ./
# create trigger
# test adding a bid without a user
# test adding an auction with a seller who is not a user
# test bids and auctions with existing user
# test that all current auctions and bids' users exist
class ConstraintTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        file = open('../src/create.sql')
        sql = file.read()
        file.close()
        self.cursor.executescript(sql)

        self.import_dat(
            '../src/dat/categories.dat',
            'category',
            [
                'id',
                'name'
            ]
        )

        self.import_dat(
            '../src/dat/countries.dat',
            'country',
            [
                'id',
                'name'
            ]
        )

        self.import_dat(
            '../src/dat/locations.dat',
            'location',
            [
                'id',
                'name',
                'country_name'
            ]
        )

        self.import_dat(
            '../src/dat/users.dat',
            'user',
            [
                'id',
                'rating',
                'location_name',
                'country_name'
            ]
        )
        self.import_dat(
            '../src/dat/bids.dat',
            'bid',
            [
                'auction_id',
                'user_id',
                'time',
                'amount'
            ]
        )
        self.import_dat(
            '../src/dat/auctions.dat',
            'auction',
            [
                'id',
                'name',
                'starting_price',
                'start',
                'end',
                'description',
                'buy_price',
                'seller_id'
            ]
        )
        self.import_dat(
                '../src/dat/join_auction_category.dat',
                'join_auction_category',
                [
                    'id',
                    'auction_id',
                    'category',
                ]
            )

        file = open('../src/normalize.sql')
        sql = file.read()
        file.close()
        self.cursor.executescript(sql)

    def tearDown(self) -> None:
        self.conn.close()

    def test_import_all_categories_with_unique_id(self):
        self.assertEqual(
            1042,
            self.conn.execute(
                "select count(*) "
                "from category;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from category "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_countries_with_unique_id(self):
        self.assertEqual(
            44,
            self.conn.execute(
                "select count(*) "
                "from country;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from country "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_locations_with_unique_id(self):
        self.assertEqual(
            9007,
            self.conn.execute(
                "select count(*) "
                "from location;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from location "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_import_all_auction_category_joins(self):
        self.assertEqual(
            90269,
            self.conn.execute(
                "select count(*) "
                "from join_auction_category;"
            ).fetchall()[0][0]
        )
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from join_auction_category "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_no_two_users_share_same_id(self):
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from user "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_all_bids_import(self):
        self.assertEqual(
            9874,
            self.conn.execute(
                "select count(*) "
                "from bid;"
            ).fetchall()[0][0]
        )

    def test_bid_composite_primary_key_is_unique(self):
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select auction_id, user_id, amount "
                "from bid "
                "group by auction_id, user_id, amount "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_all_auctions_import(self):
        self.assertEqual(
            19532,
            self.conn.execute(
                "select count(*) "
                "from auction;"
            ).fetchall()[0][0]
        )

    def test_auction_id_is_unique(self):
        self.assertCountEqual(
            [],
            self.conn.executescript(
                "select id "
                "from auction "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_new_bid_with_existing_user(self):
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]
        auction_id = self.cursor.execute(
            "select id "
            "from auction;"
        ).fetchone()[0]
        self.cursor.execute(
            f'insert into bid '
            f'values ({auction_id}, \'{user_id}\', \'2001-12-13 16:28:34\', 7.75);'
        )
        self.assertEqual(
            9875,
            self.conn.execute(
                "select count(*) "
                "from bid;"
            ).fetchall()[0][0]
        )

    def test_bidding_with_new_user_triggers_user_creation(self):
        new_user = 'newuserwhoisdefinitelynotalreadyinthedatabase'
        self.assertEqual(
            [],
            self.cursor.execute(
                f'select * '
                f'from user '
                f'where id=\'{new_user}\';'
            ).fetchall()
        )

        auction_id = self.cursor.execute(
            "select id "
            "from auction;"
        ).fetchone()[0]
        self.cursor.execute(
            f'insert into bid '
            f'values ({auction_id}, \'{new_user}\', \'2001-12-13 16:28:34\', 7.75);'
        )

        self.assertEqual(
            1,
            len(
                self.cursor.execute(
                    f'select * '
                    f'from user '
                    f'where id=\'{new_user}\';'
                ).fetchall()
            )
        )

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
        file = open('../src/query2.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            80,
            users[0][0]
        )

    def test_query_3_auctions_with_four_categories(self):
        file = open('../src/query3.sql')
        sql = file.read()
        file.close()
        auctions = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            8365,
            auctions[0][0]
        )

    def test_query_4_auction_with_highest_bid(self):
        file = open('../src/query4.sql')
        sql = file.read()
        file.close()
        auctions = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            1046740686,
            auctions[0][0]
        )

    def test_query_5_sellers_with_ratings_over_1000(self):
        file = open('../src/query5.sql')
        sql = file.read()
        file.close()
        sellers = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            3130,
            sellers[0][0]
        )

    def test_query_6_users_that_are_bidders_and_sellers(self):
        file = open('../src/query6.sql')
        sql = file.read()
        file.close()
        users = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            6717,
            users[0][0]
        )

    def test_query_7_categories_with_bids_over_100(self):
        file = open('../src/query7.sql')
        sql = file.read()
        file.close()
        categories = self.cursor.execute(
            sql
        ).fetchall()
        self.assertEqual(
            150,
            categories[0][0]
        )

    def import_dat(self, dat_path, table_name, column_names):
        file = open(dat_path, 'r')
        dat_file = csv.reader(
            file,
            delimiter='|'
        )
        concatenated_column_names = ','.join(column_names)
        for i in range(0, len(column_names)):
            if i == 0:
                concatenated_value_headers = f'?'
                if len(column_names) == 1:
                    break
            else:
                concatenated_value_headers = f'{concatenated_value_headers},?'

        for row in dat_file:
            to_db = []
            while len(row) > 0:
                to_db.insert(0, row.pop())
            self.cursor.execute(
                f'insert into {table_name} ({concatenated_column_names}) '
                f'values ({concatenated_value_headers});', to_db
            )
        self.conn.commit()
        file.close()


if __name__ == '__main__':
    unittest.main()
