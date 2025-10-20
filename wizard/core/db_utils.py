# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module provides utility functions for interacting with a PostgreSQL database.
It includes functions for creating databases and tables, inserting, retrieving, 
updating, and deleting rows, as well as checking the existence of databases and 
tables. The module relies on an external `db_core` module for database connections 
and execution of SQL commands.

Key Features:
- Create and manage databases and tables.
- Perform CRUD (Create, Read, Update, Delete) operations on database tables.
- Check the existence of databases, tables, and specific records.
- Retrieve table descriptions and list all tables in the database.

Dependencies:
- Python's `logging` module for logging debug and error messages.
- `db_core` module for database connection and execution of SQL commands.

Note:
- Ensure that the `db_core` module is properly implemented and accessible.
- The `execute_sql` function is a wrapper around the `db_core` module's database 
    access singleton for executing SQL commands.
"""

# Python modules
import logging

# Wizard modules
from wizard.core import db_core

logger = logging.getLogger(__name__)


# Function to create a new database
def create_database(database):
    return db_core.create_database(database)

# Function to create a new table in the specified database


def create_table(database, cmd):
    return db_core.create_table(database, cmd)


def create_row(level, table, columns, datas):
    """
    Inserts a new row into the specified database table and returns the ID of the inserted row.

    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the table where the row will be inserted.
        columns (list of str): A list of column names for the table.
        datas (list): A list of values corresponding to the columns to be inserted.

    Returns:
        int: The ID of the newly inserted row.

    Notes:
        - The function constructs an SQL `INSERT INTO` statement dynamically using the provided
          table name and columns.
        - The `datas` parameter should match the order and count of the `columns` parameter.
        - The function relies on an external `execute_sql` function to execute the SQL command.
    """
    # Construct the SQL command for inserting a new row into the specified table
    sql_cmd = f''' INSERT INTO {table}('''
    sql_cmd += (',').join(columns)  # Add the column names to the SQL command
    sql_cmd += ') VALUES('

    # Create a list of placeholders for the data values
    data_abstract_list = []
    for item in columns:
        # Use '%s' as a placeholder for each column value
        data_abstract_list.append('%s')

    # Add the placeholders to the SQL command
    sql_cmd += (',').join(data_abstract_list)
    # Specify that the ID of the inserted row should be returned
    sql_cmd += ') RETURNING id;'

    # Execute the SQL command and return the ID of the newly inserted row
    return execute_sql(sql_cmd, level, 0, datas, 1)


def get_rows(level, table, column='*', order='id', sort=''):
    """
    Retrieve rows from a specified database table with optional sorting.

    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the table to query.
        column (str, optional): The column(s) to select. Defaults to '*', which selects all columns.
        order (str, optional): The column to order the results by. Defaults to 'id'.
        sort (str, optional): The sorting direction, such as 'ASC' for ascending or 'DESC' for descending. Defaults to an empty string.

    Returns:
        list or dict: The query result. Returns a list of rows if specific columns are selected, 
                      or a dictionary if all columns are selected.
    """
    sql_cmd = f''' SELECT {column} FROM {table} ORDER BY {order} {sort}'''
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict)


def get_row_by_column_data(level,
                           table,
                           column_tuple,
                           column='*',
                           order='id'):
    """
    Retrieve rows from a database table based on a specific column value.

    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        column_tuple (tuple): A tuple containing the column name and the value to filter by.
                                Example: ('column_name', 'value').
        column (str or list, optional): The column(s) to retrieve. Defaults to '*'.
                                        If a list is provided, multiple columns will be selected.

    Returns:
        list or dict: The query result. If `column` is '*', the result is returned as a list of dictionaries.
                        Otherwise, it is returned as a list of tuples.

    Notes:
        - The query results are ordered by the `id` column.
        - The function uses parameterized queries to prevent SQL injection.
    """
    if type(column) == list:
        sql_cmd = f"SELECT {(', ').join(column)} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY {order}"
    else:
        sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY {order}"
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))


def get_row_by_column_part_data(level,
                                table,
                                column_tuple,
                                column='*'):
    """
    Retrieve rows from a database table based on a partial match in a specified column.
    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        column_tuple (tuple): A tuple containing the column name and the partial value to match.
                                Example: ('column_name', 'partial_value')
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).
    Returns:
        list or dict: The query result. If `column` is '*', the result is returned as a list of dictionaries.
                        Otherwise, it is returned as a list of tuples.
    """

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} ILIKE %s ORDER BY id"
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict, (f"%{column_tuple[1]}%",))


def get_row_by_column_part_data_and_data(level,
                                         table,
                                         column_tuple,
                                         second_column_tuple,
                                         column='*'):
    """
    Retrieves rows from a database table based on partial matching of one column 
    and exact matching of another column, with an option to specify the columns 
    to retrieve.
    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        column_tuple (tuple): A tuple containing the column name (str) and the 
            partial value (str) to match using a case-insensitive LIKE query.
        second_column_tuple (tuple): A tuple containing the column name (str) 
            and the exact value (str) to match.
        column (str, optional): The column(s) to retrieve in the SELECT query. 
            Defaults to '*' (all columns).
    Returns:
        list or dict: The query result. If `column` is '*', the result is 
            returned as a list of dictionaries. Otherwise, it is returned as 
            a list of tuples.
    Notes:
        - The query uses ILIKE for case-insensitive partial matching on the 
            first column and exact matching on the second column.
        - The results are ordered by the `id` column.
    """

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} ILIKE %s AND {second_column_tuple[0]}=%s ORDER BY id;"
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict, (f"%{column_tuple[1]}%", second_column_tuple[1]))


def get_last_row_by_column_data(level,
                                table,
                                column_tuple,
                                column='*'):
    """
    Retrieve the last row from a database table based on a specific column value.
    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        column_tuple (tuple): A tuple containing the column name and the value to filter by.
                                Example: ('column_name', 'value_to_match')
        column (str, optional): The column(s) to retrieve. Defaults to '*', which retrieves all columns.
    Returns:
        dict or list: The result of the query. If `column` is '*', the result is returned as a dictionary.
                        Otherwise, it is returned as a list.
    Notes:
        - The query retrieves the last row (based on descending order of the `id` column) that matches
            the specified column value.
        - The `execute_sql` function is assumed to handle the execution of the SQL query and return the result.
    """

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY id DESC LIMIT 1;"
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))


def check_existence_by_multiple_data(level,
                                     table,
                                     columns_tuple,
                                     data_tuple):
    """
    Checks the existence of a record in a database table based on multiple column values.
    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        columns_tuple (tuple): A tuple containing the names of the columns to filter by.
        data_tuple (tuple): A tuple containing the values corresponding to the columns in `columns_tuple`.
    Returns:
        Any: The result of the SQL query execution, typically the `id` of the matching record if found.
    Notes:
        - The function constructs an SQL query to check for a record where the specified columns match the provided values.
        - The query results are ordered by the `id` column.
        - This function relies on an external `execute_sql` function to execute the query.
    """

    sql_cmd = f"SELECT id FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s ORDER BY id;"
    return execute_sql(sql_cmd, level, 0, data_tuple)


def check_existence(level,
                    table,
                    column,
                    data):
    """
    Checks the existence of a record in a specified database table.
    Args:
        level (int): The database connection level or identifier.
        table (str): The name of the database table to query.
        column (str): The column name to filter the query by.
        data (Any): The value to match in the specified column.
    Returns:
        list: A list of IDs from the table where the column matches the given data.
                Returns an empty list if no matches are found.
    Note:
        This function assumes the existence of an `execute_sql` function that
        executes the SQL query and handles the database interaction.
    """
    sql_cmd = f"SELECT id FROM {table} WHERE {column}=%s ORDER BY id;"
    return execute_sql(sql_cmd, level, 0, (data,))


def get_row_by_multiple_data(level,
                             table,
                             columns_tuple,
                             data_tuple,
                             column='*'):
    """
    Retrieve a row from a database table based on multiple column values.
    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to query.
        columns_tuple (tuple): A tuple containing the names of the columns to filter by.
        data_tuple (tuple): A tuple containing the values corresponding to the columns in `columns_tuple`.
        column (str, optional): The specific column(s) to retrieve. Defaults to '*' (all columns).
    Returns:
        list or dict: The query result. If `column` is '*', the result is returned as a dictionary.
                        Otherwise, it is returned as a list.
    """
    sql_cmd = f"SELECT {column} FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s ORDER BY id;"
    if column != '*':
        as_dict = 0
    else:
        as_dict = 1
    return execute_sql(sql_cmd, level, as_dict, data_tuple)


def update_data(level,
                table,
                set_tuple,
                where_tuple):
    """
    Updates a record in the specified database table.
    Args:
        level (int): The database connection level or identifier.
        table (str): The name of the table to update.
        set_tuple (tuple): A tuple containing the column name to update and its new value.
                            Example: ('column_name', new_value)
        where_tuple (tuple): A tuple containing the column name for the WHERE clause and its value.
                                Example: ('column_name', value)
    Returns:
        Any: The result of the `execute_sql` function, which executes the SQL command.
    Example:
        update_data(
            level=1,
            table="users",
            set_tuple=("username", "new_username"),
            where_tuple=("id", 123)
        )
        This will execute:
        UPDATE users SET username = 'new_username' WHERE id = 123
    """
    sql_cmd = f''' UPDATE {table}'''
    sql_cmd += f''' SET {set_tuple[0]} = %s'''
    sql_cmd += f''' WHERE {where_tuple[0]} = %s'''
    return execute_sql(sql_cmd, level, 0, (set_tuple[1], where_tuple[1]), 0)


def update_multiple_data(level, table, set_values):
    """
    Updates multiple rows in a database table with specified values.

    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the database table to update.
        set_values (list of tuples): A list of tuples where each tuple contains:
            - The ID of the row to update (value[0]).
            - The column name to update (value[1]).
            - The new value to set in the column (value[2]).

    Returns:
        Any: The result of the `execute_sql` function, which executes the SQL command.

    Notes:
        - This function constructs an SQL command to update multiple rows in the specified table.
        - The `execute_sql` function is assumed to handle the execution of the SQL command.
        - Ensure that the `set_values` list is properly formatted to avoid SQL injection risks.
    """
    sql_cmd = ''
    all_params = tuple()
    for value in set_values:
        sql_cmd += f'''UPDATE {table} SET {value[1]} = %s WHERE id = %s;'''
        all_params = all_params+(value[2],)
        all_params = all_params+(value[0],)
    return execute_sql(sql_cmd, level, 0, all_params, 0)


def delete_row(level, table, id, column='id'):
    """
    Deletes a row from the specified table in the database.

    Args:
        level (str): The database connection level or identifier.
        table (str): The name of the table from which the row will be deleted.
        id (Any): The value of the column used to identify the row to delete.
        column (str, optional): The column name used to identify the row. Defaults to 'id'.

    Returns:
        Any: The result of the `execute_sql` function, which executes the SQL command.
    """
    sql_cmd = f'DELETE FROM {table} WHERE {column}=%s'
    return execute_sql(sql_cmd, level, 0, (id,), 0)


def delete_rows(level, table):
    """
    Deletes all rows from the specified table in the database.

    Args:
        level (int): The database level or connection identifier to execute the SQL command.
        table (str): The name of the table from which all rows will be deleted.

    Returns:
        Any: The result of the `execute_sql` function, which executes the SQL command.
    """
    sql_cmd = f'DELETE FROM {table}'
    return execute_sql(sql_cmd, level, 0, None, 0)


def check_database_existence(database):
    """
    Checks if a specified database exists in the PostgreSQL server.

    Args:
        database (str): The name of the database to check.

    Returns:
        int or None: Returns 1 if the database exists, None otherwise.

    Logs:
        Logs a debug message indicating whether the database exists or not.

    Notes:
        - This function assumes that the `db_core.create_connection()` method is available 
          and returns a valid connection object to the PostgreSQL server.
        - The connection is set to autocommit mode.
        - The function closes the connection after execution.
    """
    conn = db_core.create_connection()
    if conn is None:
        return
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    list_database = cur.fetchall()
    conn.close()
    if (database,) not in list_database:
        logger.debug("'{}' Database doesn't exist.".format(database))
        return
    logger.debug("'{}' Database already exist".format(database))
    return 1


def get_table_description(level, table):
    """
    Retrieves the description of a database table, including column names and their data types.

    Args:
        level (str): The database connection level or identifier to execute the SQL query.
        table (str): The name of the table whose description is to be retrieved.

    Returns:
        list: A list of tuples where each tuple contains the column name and its data type.

    Note:
        This function relies on the `execute_sql` function to execute the SQL query.
        Ensure that the `execute_sql` function is properly implemented and accessible.
    """
    sql_cmd = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' order by ORDINAL_POSITION;"
    return execute_sql(sql_cmd, level, 1)


def get_tables(level):
    """
    Retrieves the names of all tables in the 'public' schema of the database.

    Args:
        level (int): The database connection level or context to execute the SQL command.

    Returns:
        list: A list of table names retrieved from the 'public' schema.

    Notes:
        - This function relies on the `execute_sql` function to execute the SQL command.
        - The `execute_sql` function is expected to handle the database connection and query execution.
    """
    sql_cmd = "SELECT table_name FROM information_schema.tables WHERE (table_schema = 'public')"
    return execute_sql(sql_cmd, level, 1)


def execute_sql(sql, level, as_dict, data=None, fetch=2):
    """
    Executes an SQL command using the database access singleton.

    Args:
        sql (str): The SQL query to be executed.
        level (str): The access level or context for the SQL execution.
        as_dict (bool): Whether to return the results as a dictionary.
        data (Optional[dict]): The data to be passed as parameters to the SQL query. Defaults to None.
        fetch (int): The fetch mode for the query results. 
                     0 = No fetch, 1 = Fetch one row, 2 = Fetch all rows. Defaults to 2.

    Returns:
        Any: The result of the SQL execution, format depends on `as_dict` and `fetch` parameters.
    """
    return db_core.db_access_singleton().execute_signal(level=level,
                                                        sql_cmd=sql,
                                                        as_dict=as_dict,
                                                        data=data,
                                                        fetch=fetch)


def modify_db_name(level, db_name):
    """
    Modifies the database name in the DB server (db_core) based on the specified level.

    Parameters:
        level (str): The level of the database to modify. 
                     Accepted values are 'repository' or 'project'.
        db_name (str): The name of the database to set.

    Returns:
        bool: True if the database name was successfully modified, False otherwise.

    Raises:
        ValueError: If the provided level is not 'repository' or 'project'.

    Notes:
        This function interacts with the database access singleton to set the 
        repository or project database name based on the provided level.
    """
    if level == 'repository':
        return db_core.db_access_singleton().set_repository(db_name)
    elif level == 'project':
        return db_core.db_access_singleton().set_project(db_name)
