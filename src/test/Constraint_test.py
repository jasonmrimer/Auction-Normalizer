import unittest
import datetime
from test.TestDatabase import *
from test.helper import *


class TestConstraints(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = create_test_database()
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_no_two_users_share_same_id(self):
        self.is_table_unique_on_columns(
            'user',
            'id'
        )

    def test_cannot_add_duplicate_user(self):
        self.denies_duplicates(
            'user',
            'id',
            ['id', 'rating', 'location']
        )

    def test_auction_id_is_unique(self):
        self.is_table_unique_on_columns(
            'auction',
            'id'
        )

    def test_cannot_add_duplicate_auction(self):
        self.denies_duplicates(
            'auction',
            'id',
            [
                'id',
                'name',
                'starting_price',
                'start',
                'end',
                'description',
                'buy_price',
                'seller_id',
                'number_of_bids',
                'highest_bid'
            ]
        )

    def test_cannot_add_auctions_with_end_time_before_or_equal_to_start_time(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select * "
                "from auction "
                "where end <= start;"
            ).fetchall()
        )

        auction_count = count_from_table(self.cursor, 'auction')

        seller_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]

        try:
            self.cursor.execute(
                f"insert into auction "
                f"values ("
                f"null, "
                f"'name', "
                f"0.01, "
                f"'2000-01-01 00:00:01', "
                f"'1999-12-31 23:59:59', "
                f"'description', "
                f"10.00, "
                f"'{seller_id}', "
                f"0, "
                f"0.00);"
            )
            self.assertTrue(
                False,
                "Database failed to deny auction with end time before start time."
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "CHECK constraint failed: auction"
                )
            )

        self.assertEqual(
            auction_count,
            count_from_table(self.cursor, 'auction')
        )

    def test_bid_composite_primary_key_is_unique(self):
        self.is_table_unique_on_columns(
            'bid',
            ['auction_id', 'user_id', 'amount']
        )

    def test_bid_cannot_be_at_the_same_time_for_same_auction(self):
        bid_count = count_from_table(
            self.cursor,
            'bid'
        )
        self.is_table_unique_on_columns(
            'bid',
            ['auction_id', 'time']
        )
        auction_id = self.cursor.execute(
            "select id "
            "from auction;"
        ).fetchone()[0]
        user_ids = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchall()
        first_user_id = user_ids[0][0]
        second_user_id = user_ids[1][0]
        time = now()
        self.cursor.execute(
            f"insert into bid "
            f"values ("
            f"{auction_id}, "
            f"'{first_user_id}', "
            f"'{time}', "
            f"123456);"
        )
        bid_count += 1
        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )
        try:
            self.cursor.execute(
                f"insert into bid "
                f"values ("
                f"{auction_id}, "
                f"'{second_user_id}', "
                f"'{time}', "
                f"1234567);"
            )
            self.assertTrue(
                False,
                "Database failed to deny bid for the same auction at the same time"
            )
        except sqlite3.IntegrityError as e:
            self.assertEqual(
                str(e),
                "UNIQUE constraint failed: bid.auction_id, bid.time"
            )

        self.assertEqual(
            bid_count,
            count_from_table(
                self.cursor,
                'bid'
            )
        )

    def test_location_id_is_unique(self):
        self.is_table_unique_on_columns(
            'location',
            'id'
        )

    def test_cannot_add_duplicate_location(self):
        self.denies_duplicates(
            'location',
            [
                'name',
                'country_id'
            ],
            [
                'id',
                'name',
                'country_id'
            ]
        )

    def test_country_id_is_unique(self):
        self.is_table_unique_on_columns(
            'country',
            'id'
        )

    def test_cannot_add_duplicate_country(self):
        self.denies_duplicates(
            'country',
            'name',
            ['id', 'name']
        )

    def test_category_name_is_unique(self):
        self.is_table_unique_on_columns(
            'category',
            'name'
        )

    def test_auction_cannot_belong_to_category_more_than_once(self):
        self.is_table_unique_on_columns(
            'join_auction_category',
            ['auction_id', 'category_id']
        )

        self.denies_duplicates(
            'join_auction_category',
            ['auction_id', 'category_id'],
            ['id', 'auction_id', 'category_id']
        )

    def test_cannot_add_duplicate_category(self):
        self.denies_duplicates(
            'category',
            'name',
            ['id', 'name']
        )

    def test_items_must_exist_for_category_matches(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select auction_id "
                "from join_auction_category "
                "where not exists("
                "select id "
                "from auction"
                ");"
            ).fetchall()
        )

        join_count = count_from_table(self.cursor, 'join_auction_category')

        try:
            self.cursor.execute(
                "insert into join_auction_category "
                "values (null, 123456789, 1);"
            )
            self.assertTrue(
                False,
                f"Database failed to throw error on Foreign Key for auction ID: 123456789"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "FOREIGN KEY constraint failed"
                )
            )

        self.assertEqual(
            join_count,
            count_from_table(self.cursor, 'join_auction_category')
        )

    def test_every_bid_must_correspond_to_an_auction(self):
        self.assertEqual(
            [],
            self.cursor.execute(
                "select auction_id "
                "from bid "
                "where not exists("
                "select id "
                "from auction"
                ");"
            ).fetchall()
        )
        user_id = self.cursor.execute(
            "select id "
            "from user;"
        ).fetchone()[0]

        try:
            self.cursor.execute(
                "insert into bid "
                f"values (null, '{user_id}', '2001-12-13 16:28:34','7.75');"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "NOT NULL constraint failed: bid.auction_id"
                )
            )

        self.assertEqual(
            [],
            self.cursor.execute(
                "select * "
                "from auction "
                "where id=123456789"
            ).fetchall()
        )

        try:
            self.cursor.execute(
                "insert into bid "
                f"values (123456789, '{user_id}', '2001-12-13 16:28:34','7.75');"
            )
        except sqlite3.IntegrityError as e:
            self.assertTrue(
                str(e).__contains__(
                    "FOREIGN KEY constraint failed"
                )
            )

    def denies_duplicates(
            self,
            table_name,
            unique_columns,
            column_names
    ):
        item_count = count_from_table(self.cursor, table_name)

        if type(unique_columns) == list:
            for column in range(0, len(unique_columns)):
                if column == 0:
                    concatenated_uniques = f'{unique_columns[column]}'
                    if len(unique_columns) == 1:
                        break
                else:
                    concatenated_uniques = f'{concatenated_uniques},{unique_columns[column]}'
            existing_item = self.cursor.execute(
                f"select {concatenated_uniques} "
                f"from {table_name};"
            ).fetchone()
        else:
            existing_item = self.cursor.execute(
                f"select {unique_columns} "
                f"from {table_name};"
            ).fetchone()[0]

        for column_index in range(0, len(column_names)):
            column_name = column_names[column_index]
            if type(unique_columns) == list:
                if column_index == 0:
                    if unique_columns.__contains__(column_name):
                        concatenated_values = f"'{existing_item[unique_columns.index(column_name)]}'"
                    else:
                        concatenated_values = f"'123456789'"
                else:
                    if unique_columns.__contains__(column_name):
                        concatenated_values = \
                            f"{concatenated_values}, " \
                                f"'{existing_item[unique_columns.index(column_name)]}'"
                    else:
                        concatenated_values = f"{concatenated_values}, '123456789'"

            else:
                if column_index == 0:
                    if column_name == unique_columns:
                        concatenated_values = f"'{existing_item}'"
                    else:
                        if column_name == 'start':
                            concatenated_values = f"'{now()}"
                        elif column_name == 'end':
                            concatenated_values = f"'{now(1)}"
                        else:
                            concatenated_values = f"'123456789'"
                    if len(column_names) == 1:
                        break
                else:
                    if column_name == unique_columns:
                        concatenated_values = f"{concatenated_values}, '{existing_item}'"
                    elif column_name == 'start':
                        concatenated_values = f"{concatenated_values}, " \
                            f"'{now()}'"
                    elif column_name == 'end':
                        concatenated_values = f"{concatenated_values}, " \
                            f"'{now(1)}'"
                    else:
                        concatenated_values = f"{concatenated_values}, '123456789'"

        try:
            self.cursor.execute(
                f'insert into {table_name} '
                f'values ({concatenated_values});'
            )
        except sqlite3.IntegrityError as e:
            if type(unique_columns) == list:
                for column_index in range(0, len(unique_columns)):
                    if column_index == 0:
                        concatenated_error = \
                            f"{table_name}" \
                                f".{unique_columns[column_index]}"
                    else:
                        concatenated_error = \
                            f"{concatenated_error}" \
                                f", {table_name}" \
                                f".{unique_columns[column_index]}"

                self.assertTrue(
                    str(e).__contains__(f"UNIQUE constraint failed: {concatenated_error}")
                )
            else:
                self.assertTrue(
                    str(e).__contains__(f"UNIQUE constraint failed: {table_name}.{unique_columns}")
                )

        self.assertEqual(
            item_count,
            count_from_table(self.cursor, table_name)
        )

    def is_table_unique_on_columns(
            self,
            table_name,
            unique_on_column_names
    ):
        self.assertEqual(
            [],
            duplicate_rows_from_table(
                self.cursor,
                table_name,
                unique_on_column_names
            )
        )


if __name__ == '__main__':
    unittest.main()
