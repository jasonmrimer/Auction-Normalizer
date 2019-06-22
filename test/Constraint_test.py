import unittest
import sqlite3

from test.TestDatabase import create_test_database


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = create_test_database()
        self.cursor = self.conn.cursor()

    def tearDown(self) -> None:
        self.conn.close()

    def test_no_two_users_share_same_id(self):
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select id "
                "from user "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_cannot_add_duplicate_user(self):
        self.denies_duplicates(
            'user',
            'id',
            ['id', 'rating', 'location']
        )

    def test_auction_id_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select id "
                "from auction "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
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

    def test_bid_composite_primary_key_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select auction_id, user_id, amount "
                "from bid "
                "group by auction_id, user_id, amount "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_location_id_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select id "
                "from location "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
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
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select id "
                "from country "
                "group by id "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_category_name_is_unique(self):
        self.assertCountEqual(
            [],
            self.cursor.execute(
                "select name "
                "from category "
                "group by name "
                "having count (*) > 1;"
            ).fetchall()
        )

    def test_cannot_add_duplicate_category(self):
        self.denies_duplicates(
            'category',
            'name',
            ['id', 'name']
        )

    def denies_duplicates(
            self,
            table_name,
            unique_columns,
            column_names
    ):
        item_count = self.cursor.execute(
            "select count(*) "
            f"from {table_name};"
        ).fetchone()[0]

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
            if type(unique_columns) == list:
                column_name = column_names[column_index]
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
                    if column_names[column_index] == unique_columns:
                        concatenated_values = f"'{existing_item}'"
                    else:
                        concatenated_values = f"'123456789'"
                    if len(column_names) == 1:
                        break
                else:
                    if column_names[column_index] == unique_columns:
                        concatenated_values = f"{concatenated_values}, '{existing_item}'"
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
            self.cursor.execute(
                "select count(*) "
                f"from {table_name};"
            ).fetchone()[0]
        )


if __name__ == '__main__':
    unittest.main()
