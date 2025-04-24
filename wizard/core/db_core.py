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
This module provides core database functionalities for the Wizard application.
It includes classes and functions for managing database connections, executing
SQL commands, and handling database-related operations such as creating databases
and tables. The module uses PostgreSQL as the database backend and includes
retry logic for handling connection issues.

Classes:
    Singleton: A metaclass for implementing the Singleton design pattern.
    db_access_singleton: A singleton class for managing database access and executing SQL commands.

Functions:
    create_connection(database=None): Establishes a connection to a PostgreSQL database.
    try_connection(DNS): Attempts to establish a connection to a PostgreSQL server.
    create_database(database): Creates a new PostgreSQL database with the specified name.
    create_table(database, cmd): Creates a table in the specified database by executing the provided SQL command.

Dependencies:
    - Python modules: time, logging
    - PostgreSQL modules: psycopg2, psycopg2.extras
    - Wizard modules: environment

Logging:
    The module uses Python's logging library to log informational messages, warnings,
    and errors related to database operations.
"""


# Python modules
import time
import logging

# PostgreSQL python modules
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Wizard modules
from wizard.core import environment

logger = logging.getLogger(__name__)


class Singleton(type):
    """
    A metaclass for implementing the Singleton design pattern.
    This metaclass ensures that a class using it will only have one instance.
    If an instance of the class already exists, it returns the existing instance
    instead of creating a new one.
    Attributes:
        _instances (dict): A dictionary to store the single instance of each class
                           that uses this metaclass.
    Methods:
        __call__(cls, *args, **kwargs):
            Overrides the default behavior of creating a new instance. If an
            instance of the class already exists, it returns the existing instance.
            Otherwise, it creates a new instance and stores it in the `_instances`
            dictionary.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class db_access_singleton(metaclass=Singleton):
    """
    A singleton class for managing database access and executing SQL commands.
    This class provides methods to set the repository and project connections,
    and execute SQL commands with retry logic. It supports both repository-level
    and project-level database connections.
    Attributes:
        project_name (str): The name of the project database.
        project_conn (object): The connection object for the project database.
        repository (str): The repository database connection string.
        repository_conn (object): The connection object for the repository database.
    Methods:
        set_repository(repository):
            Sets the repository connection string and resets the repository connection.
        set_project(project_name):
            Sets the project name and resets the project connection.
        execute_signal(level, sql_cmd, as_dict=1, data=None, fetch=2):
            Executes an SQL command on the specified database level (repository or project).
            Supports fetching results as a dictionary or a list, with retry logic for connection issues.
    """

    def __init__(self):
        """
        Initializes the db_access_singleton instance.
        Sets up initial values for project and repository connections.
        """
        super(db_access_singleton, self).__init__()
        self.project_name = None
        self.project_conn = None
        self.repository = None
        self.repository_conn = None

    def set_repository(self, repository):
        """
        Sets the repository connection string and resets the repository connection.
        Args:
            repository (str): The repository database connection string.
        """
        self.repository = repository
        self.repository_conn = None

    def set_project(self, project_name):
        """
        Sets the project name and initializes the project connection to None.

        Args:
            project_name (str): The name of the project to set.
        """
        self.project_name = project_name
        self.project_conn = None

    def execute_signal(self, level,
                       sql_cmd,
                       as_dict=1,
                       data=None,
                       fetch=2):
        """
        Executes a SQL command on the specified database connection.

        Parameters:
            level (str): Specifies the database connection to use. 
                         Use 'repository' for the repository database or any other value for the project database.
            sql_cmd (str): The SQL command to execute.
            as_dict (bool, optional): If set to 1 (default), fetches results as a dictionary. 
                                      If set to 0, fetches results as a list.
            data (tuple, optional): Parameters to pass to the SQL command. Defaults to None.
            fetch (int, optional): Specifies the fetch behavior:
                                   - 2 (default): Fetch all rows.
                                   - 1: Fetch a single row.
                                   - 0: No fetch, return 1 on success.

        Returns:
            list[dict] | list | dict | int | None: 
                - If `fetch` is 2 and `as_dict` is 1, returns a list of dictionaries (rows).
                - If `fetch` is 2 and `as_dict` is 0, returns a list of values.
                - If `fetch` is 1, returns the first row's first column value.
                - If `fetch` is 0, returns 1 on success.
                - Returns None if the connection fails or an error occurs.

        Raises:
            Logs errors if the database connection fails or the SQL execution encounters an issue.

        Notes:
            - Retries up to 5 times if the database connection fails.
            - Logs an error and returns None if the maximum retry count is reached.
            - Automatically creates a connection if it does not exist for the specified level.
        """
        rows = None
        retry_count = 0

        while rows is None:
            try:
                # Determine the connection level (repository or project)
                if level == 'repository':
                    # Create a repository connection if it doesn't exist
                    if not self.repository_conn:
                        if self.repository:
                            self.repository_conn = create_connection(
                                self.repository)
                    conn = self.repository_conn
                else:
                    # Create a project connection if it doesn't exist
                    if not self.project_conn:
                        if self.project_name:
                            self.project_conn = create_connection(
                                self.project_name)
                    conn = self.project_conn

                # If a connection is established, execute the SQL command
                if conn:
                    rows = None
                    # Use a dictionary cursor if as_dict is True
                    if as_dict:
                        cursor = conn.cursor(
                            cursor_factory=psycopg2.extras.RealDictCursor)
                    else:
                        cursor = conn.cursor()

                    # Execute the SQL command with or without data
                    if data:
                        cursor.execute(sql_cmd, data)
                    else:
                        cursor.execute(sql_cmd)

                    # Fetch results based on the fetch parameter
                    if fetch == 2:
                        rows = cursor.fetchall()
                        cursor.close()
                    elif fetch == 1:
                        rows = cursor.fetchone()[0]
                        cursor.close()
                    else:
                        rows = 1

                    # If not fetching as a dictionary and fetch != 1, process rows
                    if not as_dict and fetch != 1:
                        if rows != 1:
                            rows = [r[0] for r in rows]

                    # Return the fetched rows
                    return rows
                else:
                    # Log an error if no connection is available
                    logger.error("No connection")
                    self.repository_conn = None
                    self.project_conn = None
            except (Exception, psycopg2.DatabaseError) as error:
                # Log the error and reset connections
                logger.error(error)
                self.repository_conn = None
                self.project_conn = None

                # Retry logic for database connection issues
                if retry_count == 5:
                    logger.error(
                        "Database max retry reached ( 5 ). Can't access database")
                    time.sleep(0.02)
                    return None
                retry_count += 1
                logger.error(
                    f"Can't reach database, retrying ( {retry_count} )")


def create_connection(database=None):
    """
    Establishes a connection to a PostgreSQL database using the provided database name.

    Args:
        database (str, optional): The name of the database to connect to. Defaults to None.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database if successful.
        None: If the connection fails.

    Logs:
        - Logs an informational message if the connection to the database is successful.
        - Logs an error message if there is an exception during the connection attempt.

    Raises:
        None: Any exceptions are caught and logged instead of being raised.
    """
    try:
        conn = psycopg2.connect(environment.get_psql_dns(), database=database)
        if conn and database:
            conn.autocommit = True
            logger.info(f"Wizard is connected to {database} database")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return


def try_connection(DNS):
    """
    Attempts to establish a connection to a PostgreSQL server using the provided DNS string.

    Args:
        DNS (str): The Data Source Name (DNS) string containing the connection details.

    Returns:
        int: Returns 1 if the connection is successful.
        None: Returns None if the connection fails due to an OperationalError.

    Logs:
        Logs an error message if the connection attempt fails, including the DNS string used.

    Raises:
        psycopg2.OperationalError: If there is an issue with the connection parameters or server.
    """
    try:
        conn = psycopg2.connect(DNS)
        if conn is not None:
            conn.close()
        return 1
    except psycopg2.OperationalError as e:
        logger.error(e)
        logger.error(
            f"Wizard could not connect to PostgreSQL server with this DNS : {DNS}")
        return


def create_database(database):
    """
    Creates a new PostgreSQL database with the specified name.

    Args:
        database (str): The name of the database to be created.

    Returns:
        int: Returns 1 if the database is successfully created.
        None: Returns None if an error occurs during the database creation.

    Raises:
        psycopg2.DatabaseError: If a database-related error occurs.

    Notes:
        - The function establishes a connection to the PostgreSQL server,
          sets the isolation level to autocommit, and executes the SQL
          command to create the database.
        - Any errors encountered during the process are logged using the
          logger.
        - The connection to the database server is closed in the `finally` block.
    """
    conn = None
    try:
        conn = create_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {database};")
        cur.close()
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return
    finally:
        if conn is not None:
            conn.close()


def create_table(database, cmd):
    """
    Creates a table in the specified database by executing the provided SQL command.

    Args:
        database (str): The path or connection string to the database.
        cmd (str): The SQL command to create the table.

    Returns:
        int: Returns 1 if the table is created successfully.
        None: Returns None if an error occurs during the operation.

    Raises:
        Exception: Logs any exception or database error encountered during execution.

    Note:
        Ensures the database connection is properly closed after the operation, 
        regardless of success or failure.
    """
    try:
        conn = create_connection(database)
        cursor = conn.cursor()
        cursor.execute(cmd)
        cursor.close()
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return
    finally:
        if conn:
            conn.close()
