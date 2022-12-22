"""
Author: Logan Maupin

The purpose of this python script is to store our methods for sending and retrieving data to our database.
This way we can store the methods here and then call them later in other projects.

The overall goal is to use OOP techniques to create clean, testable, and reusable code.
"""

import sqlite3


class Database:

    def __init__(self, file_path_and_name: str):
        self.file_path_and_name = file_path_and_name
        self.connect = sqlite3.connect(file_path_and_name)
        self.cursor = self.connect.cursor()

    @property
    def table_names(self):
        self.cursor.execute(f"""SELECT name FROM {self.file_path_and_name} WHERE type='table';""")
        tuple_of_table_names = self.cursor.fetchall()

        # Returning it this way so that it returns a list of table names instead of a list of typles of table names.
        # Which in my opinion is cleaner and easier to parse through.
        return [name for table_name in tuple_of_table_names for name in table_name]

    def log_to_DB(self, formatted_tuple: tuple, table_to_add_values_to: str):
        """
        The purpose of this function is to log our grabbed info from the get_photo function over to the database
        :param formatted_tuple: tuple containing the info that the user wishes to log to the database.
        :param table_to_add_values_to: The name of the table in the database that you want to apend an entry to.
        :returns: None
        """

        number_of_items_to_add = len(formatted_tuple)
        formatted_string = "("
        for i in range(number_of_items_to_add):
            formatted_string += "?, "
        formatted_string += ")"
        self.cursor.execute(f'INSERT INTO {table_to_add_values_to} VALUES {formatted_string}', formatted_tuple)
        self.connect.commit()

    def retrieve_values_from_table_column(self, name_of_table_to_retrieve_from: str, name_of_column: str) -> list:
        """
        Goes through a given database table and grab a column of data and return those as a list of values.

        :param name_of_table_to_retrieve_from: This will be the name of the table you want to grab values from.
        :param name_of_column: This will be the name of the column that you wish to grab all the data from.

        :return: list of values as a list, not a list of tuples but just a 1D list of each item.
        """
        self.cursor.execute(f'SELECT {name_of_column} FROM {name_of_table_to_retrieve_from}')
        tuple_of_items = self.cursor.fetchall()

        return [item for table_item in tuple_of_items for item in table_item]
