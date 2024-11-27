
# Generate Parenthesis & Media Items Database Project

This project contains solutions for creating, managing, and interacting with a database of media items using MSSQL and Python. The implementation is divided into two main parts: SQL commands and Python functions. The SQL commands handle table creation, triggers, and stored procedures, while the Python functions provide a programmatic interface to interact with the database.

## Table of Contents
- [Project Structure](#project-structure)
- [Assignment Goals](#assignment-goals)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Contact](#contact)

---

## Project Structure

The project consists of the following files:

1. **`sql.txt`**:
   - Contains MSSQL commands for table creation, triggers, and functions.
   - Organized with appropriate comments for easy navigation.

2. **`hw1.py`**:
   - Implements all required Python functions.
   - Contains a `DatabaseManager` class for database operations.

---

## Assignment Goals

1. **MSSQL Tasks**:
   - Create tables: `MediaItems` and `Similarity`.
   - Implement a trigger to auto-increment the `MID` field and calculate `TITLE_LENGTH`.
   - Define MSSQL functions for:
     - Calculating maximal distance (`MaximalDistance`).
     - Calculating similarity (`SimCalculation`).
   - Add a stored procedure (`AddSummaryItems`) for generating summary media items.

2. **Python Tasks**:
   - Define a `DatabaseManager` class to handle database connections and operations.
   - Implement functions to:
     - Insert CSV data into the database.
     - Calculate and update similarity between media items.
     - Print similar items.
     - Add summary items based on production year.

---

## Features

1. **Database Operations**:
   - Table creation and management.
   - Trigger-based automation.
   - Stored procedure execution.

2. **Similarity Calculation**:
   - Efficiently calculates the similarity between media items.

3. **Python Integration**:
   - Full control over the database via Python functions.

---

## Requirements

- Python 3.8+
- MSSQL Server
- Required Python libraries:
  - `pyodbc` (for database connections)

---

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the MSSQL database:
   - Execute the commands in `sql.txt` in your MSSQL instance.

4. Configure the `DatabaseManager`:
   - Update the database connection parameters (driver, server, username, password, database) in `hw1.py`.

---

## Usage

1. **Run Python Scripts**:
   - Execute `hw1.py` to perform database operations.

2. **Functions**:
   - **`file_to_database`**: Insert CSV data into the `MediaItems` table.
   - **`calculate_similarity`**: Calculate similarity and update the `Similarity` table.
   - **`print_similar_items`**: Print items similar to a given media item.
   - **`add_summary_items`**: Execute the stored procedure to add summary items.

---

## Contact

For any questions or clarifications, please reach out to:  
Yarin Benyamin

---

