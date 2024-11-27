import pyodbc
import csv

class DatabaseManager:
    def __init__(self, driver: str, server: str, username: str, password: str):

        # Create the connection string using the provided parameters
        self.connection_string = (
            f'DRIVER={{{driver}}};'
            f'SERVER={server};'
            f'DATABASE={username};'
            f'UID={username};'
            f'PWD={password};'
        )
    def file_to_database(self, path: str) -> None:
        """
        Reads a CSV file and inserts the content into the MediaItems table.
        The CSV file is expected to have two columns:
            1. TITLE
            2. PROD_YEAR

        Args:
            path (str): The path to the CSV file.
        """
        try:
            self.connect_to_db()
            with open(path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    title, prod_year = row
                    # Insert data without touching the identity column
                    self.cursor.execute(
                        "INSERT INTO MediaItems (TITLE, PROD_YEAR) VALUES (?, ?)",
                        title, int(prod_year)
                    )
                self.conn.commit()
        except FileNotFoundError:
            print(f"File not found: {path}")
        except ValueError as e:
            print(f"Error processing row: {e}")
        except Exception as e:
            print(f"Error reading file or inserting data: {e}")
        finally:
            self.disConnect()
       
    def calculate_similarity(self) -> None:
        """
        Calculates the similarity between every pair of items in the MediaItems table
        and inserts or updates the Similarity table.
        """
        try:
            self.connect_to_db()

            # Step 1: Get the maximal distance
            self.cursor.execute("SELECT dbo.MaximalDistance()")
            result = self.cursor.fetchone()
            if result is None:
                print("Error: MaximalDistance did not return any results.")
                return
            maximal_distance = result[0]

            # Step 2: Get all pairs of MID1, MID2 from the MediaItems table
            self.cursor.execute("""
                SELECT a.MID, b.MID 
                FROM MediaItems a
                JOIN MediaItems b ON a.MID < b.MID
            """)

            pairs = self.cursor.fetchall()

            # Step 3: Calculate similarity for each pair and insert into the Similarity table
            for row in pairs:
                MID1, MID2 = row

                # Step 3a: Calculate similarity using SimCalculation function
                self.cursor.execute("""
                    SELECT dbo.SimCalculation(?, ?, ?)
                """, MID1, MID2, maximal_distance)
                similarity = self.cursor.fetchone()[0]  # Get the similarity value

                # # Step 3b: Check if the pair already exists in the Similarity table
                # self.cursor.execute("""
                #     SELECT COUNT(*) 
                #     FROM Similarity 
                #     WHERE (MID1 = ? AND MID2 = ?) OR (MID1 = ? AND MID2 = ?)
                # """, MID1, MID2, MID2, MID1)
                # count = self.cursor.fetchone()[0]
                
                # if count == 0:  # If the pair does not exist
                    # Insert the similarity into the Similarity table
                self.cursor.execute("""
                    INSERT INTO Similarity (MID1, MID2, SIMILARITY)
                    VALUES (?, ?, ?)
                """, MID1, MID2, similarity)
            # Commit the changes to the database
            self.conn.commit()

        except pyodbc.ProgrammingError as e:
            print(f"Error executing SQL: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.disConnect()
       
    def print_similar_items(self, mid: int) -> None:

        try:
            self.connect_to_db()
            self.cursor.execute(
                """
                SELECT t2.TITLE, s.SIMILARITY 
                FROM Similarity s
                JOIN MediaItems t1 ON s.MID1 = t1.MID
                JOIN MediaItems t2 ON s.MID2 = t2.MID
                WHERE s.MID1 = ? AND s.SIMILARITY >= 0.25
                ORDER BY s.SIMILARITY ASC
                """,
                (mid,)
            )
            rows = self.cursor.fetchall()
            for row in rows:
                print(f"{row[0]} {row[1]}")
        finally:
            self.disConnect()
       

    def add_summary_items(self) -> None:
        try:
            self.connect_to_db()
            self.cursor.execute("EXEC AddSummaryItems")
            self.conn.commit()
        finally:
            self.disConnect()


    def connect_to_db(self):
        try:
            # Establish the connection to the database
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            print("Error connecting to the database:", e)
    def disConnect(self):
        self.cursor.close()
        self.conn.close()
        
    