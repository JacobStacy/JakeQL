# JakeQL 🐍📊
> A Python DBMS mimicking SQLite, designed for high-performance data handling and advanced SQL support.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)


JakeQL is a powerful, lightweight Database Management System (DBMS) built in that mimics SQLite, designed to handle multiple tables and databases seamlessly. JakeQL features robust conflict resolution with parallel transactions, supports complex joins, conditional queries, and provides full support for transaction modes, including isolation levels. It also implements rollback capabilities, aggregate functions, and the management of default values.

---

## Features ✨

- **Multi-Table & Multi-Database Management**  
  Seamlessly handles multiple tables and databases within a single environment.

- **Parallel Transactions & Conflict Resolution**  
  Supports concurrent transactions with robust conflict resolution, ensuring data consistency.

- **Advanced SQL Support**  
  Includes complex joins, conditional queries, and aggregate functions.

- **Transaction Modes & Isolation Levels**  
  Supports various transaction isolation levels, enabling you to control visibility and lock behavior.

- **Rollback Capabilities**  
  Allows safe rollbacks to maintain data integrity in case of errors.

- **Default Values & Conditional Queries**  
  Set default values and handle conditional expressions with ease.

---

## Getting Started 🚀

### Prerequisites
JakeQL is built on Python’s standard library—no external dependencies are required. Just make sure you’re using **Python 3.x**.

### Installation
Clone the repository to get started:

```bash
git clone https://github.com/JacobStacy/JakeQL
cd JakeQL
```

### Usage
JakeQL includes several scripts for testing and running SQL commands.

To run the main test script that will automatically run all test scripts and compare them to the SQLite output.
```bash
python test_project.py
```

To execute SQL statements through the CLI to test JakeQL’s capabilities use the following.
```bash
python cli.py <your_sql_file>
```

You can also add `--sqlite` to run statements directly through SQLite for comparison.

---

## Project Structure 📂

```plaintext
JakeQL/
├── test_project.py       # Main testing and execution script for JakeQL
├── cli.py                # Command-line interface for running SQL files
├── project.py            # Core JakeQL implementation
└── sql_files/            # Directory of SQL files used for testing
```

---



## License 📄

JakeQL is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgements 🌟

Special thanks to the Python and SQLite communities for their extensive documentation and tools, which helped shape this project.

---

Enjoy using **JakeQL**! 🎉