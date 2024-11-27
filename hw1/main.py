from hw1 import DatabaseManager
import pyodbc

if __name__ == '__main__':

    db = DatabaseManager("ODBC Driver 17 for SQL Server","132.72.64.124","ofirtam","s4Xw/mid")
    # db.file_to_database("films.csv")
    # db.calculate_similarity()
    # db.print_similar_items(2)
    db.add_summary_items()
