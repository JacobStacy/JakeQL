# JakeQL

A Python DBMS that mimics SQLite, designed to handle multiple tables and databases seamlessly. JakeQL features robust conflict resolution with parallel transactions, supports complex joins, conditional queries, and provides full support for transaction modes, including isolation levels. It also implements rollback capabilities, aggregate functions, and the management of default values.

## Table of Contents
- [Requirements](#requirements)
- [Usage](#usage)
- [File Structure](#file-structure)
- [project.py](#projectpy) 

## Requirements

- Python 3.x
- SQLite3

## Usage

1. To run the tests, execute the `test_project.py` script. This will automatically run a series of SQL test scripts defined in the `sql_files` list.

   ```bash
   python test_project.py
   ```

   The output will show the results of each SQL test, including any errors encountered during execution.

2. The `cli.py` script is used internally to execute the SQL commands. You can run it directly with a specific SQL file:

   ```bash
   python cli.py <sql_file> [--sqlite]
   ```

   - `<sql_file>`: The path to the SQL file you want to execute.
   - `--sqlite`: If this flag is provided, the script will use SQLite instead of the custom implementation.

## File Structure

- `test_project.py`: The main testing script that iterates through SQL test files and verifies their output.
- `cli.py`: The command-line interface for executing SQL statements from a file and displaying the results.
- `project.py`: The core module that contains the database interaction logic.
- `test1.db`: The SQLite database file used for testing. This file will be created and removed automatically during tests.

### SQL Files

The following SQL test files are included in the `sql_files` list for testing:

- Connections
- Create/Drop Table
- Isolation
- Regression
- Rollback
- Transaction Modes
- Transactions
- Delete
- Distinct
- IDs
- Insert Columns
- Joins
- Multi Insert
- Qualified
- Update
- Where
- Aggregate
- Default
- View

**Error Tests**: Some SQL files are specifically designed to trigger errors during execution. These are defined in the `error_tests` list.

## project.py

The `project.py` file defines the necessary functions and classes for interacting with the SQLite database. It handles establishing connections, executing SQL commands, and managing the lifecycle of database transactions. The functions within this module are utilized by both `test_project.py` and `cli.py` to facilitate testing and command execution.

