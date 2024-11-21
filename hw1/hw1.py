import pyodbc
import csv

class DatabaseManager:
    def __init__(self, driver: str, server: str, username: str, password: str):

        self.driver = driver
        self.server = server
        self.username = username
        self.password = password

        # Create the connection string using the provided parameters
        connection_string = (
            f'DRIVER={{{self.driver}}};'
            f'SERVER={self.server};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'DATABASE=ofirtam;'
        )

        try:
            # Establish the connection to the database
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Connection successful!")
        except pyodbc.Error as e:
            print("Error connecting to the database:", e)

    # def file_to_database(self, path: str) -> None:
    #     """
    #     Reads a CSV file and inserts the content into the MediaItems table.
    #     The CSV file is expected to have two columns:
    #         1. TITLE
    #         2. PROD_YEAR

    #     Args:
    #         path (str): The path to the CSV file.
    #     """
    #     try:
    #         with open(path, 'r') as file:
    #             reader = csv.reader(file)
    #             next(reader)  # Skip the header row
    #             self.cursor.execute("SET IDENTITY_INSERT ofirtam.dbo.MediaItems ON;")
    #             for row in reader:
    #                 title, prod_year = row
    #                 # Insert only the necessary columns
    #                 self.cursor.execute(
    #                     "INSERT INTO ofirtam.dbo.MediaItems (TITLE, PROD_YEAR) VALUES (?, ?)",
    #                     title, int(prod_year)
    #                 )
    #             self.cursor.execute("SET IDENTITY_INSERT ofirtam.dbo.MediaItems OFF;")
    #             self.conn.commit()
    #             print(f"Successfully inserted data from {path} into MediaItems table.")
    #     except FileNotFoundError:
    #         print(f"File not found: {path}")
    #     except ValueError as e:
    #         print(f"Error processing row: {e}")
    #     except Exception as e:
    #         print(f"Error reading file or inserting data: {e}")

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
            with open(path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                for row in reader:
                    title, prod_year = row
                    # Insert data without touching the identity column
                    self.cursor.execute(
                        "INSERT INTO ofirtam.dbo.MediaItems (TITLE, PROD_YEAR) VALUES (?, ?)",
                        title, int(prod_year)
                    )
                self.conn.commit()
                print(f"Successfully inserted data from {path} into MediaItems table.")
        except FileNotFoundError:
            print(f"File not found: {path}")
        except ValueError as e:
            print(f"Error processing row: {e}")
        except Exception as e:
            print(f"Error reading file or inserting data: {e}")

    def calculate_similarity(self) -> None:
        """
        Calculates the similarity between every pair of items in the MediaItems table
        and inserts or updates the Similarity table.
        """
        try:
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
                FROM ofirtam.dbo.MediaItems a
                JOIN ofirtam.dbo.MediaItems b ON a.MID < b.MID
            """)

            pairs = self.cursor.fetchall()

            # Step 3: Calculate similarity for each pair and insert into the Similarity table
            for row in pairs:
                MID1, MID2 = row
                print(f"Trying to insert MID1={MID1}, MID2={MID2}")

                # Step 3a: Calculate similarity using SimCalculation function
                self.cursor.execute("""
                    SELECT dbo.SimCalculation(?, ?, ?)
                """, MID1, MID2, maximal_distance)
                similarity = self.cursor.fetchone()[0]  # Get the similarity value

                # Step 3b: Check if the pair already exists in the Similarity table
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM Similarity 
                    WHERE (MID1 = ? AND MID2 = ?) OR (MID1 = ? AND MID2 = ?)
                """, MID1, MID2, MID2, MID1)
                count = self.cursor.fetchone()[0]
                
                if count == 0:  # If the pair does not exist
                    # Insert the similarity into the Similarity table
                    self.cursor.execute("""
                        INSERT INTO Similarity (MID1, MID2, SIMILARITY)
                        VALUES (?, ?, ?)
                    """, MID1, MID2, similarity)
                    print(f"Inserted similarity for MID1={MID1}, MID2={MID2}")
                else:
                    print(f"Pair MID1={MID1}, MID2={MID2} already exists.")

            # Commit the changes to the database
            self.conn.commit()
            print("Similarity calculation and insertion complete.")

        except pyodbc.ProgrammingError as e:
            print(f"Error executing SQL: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    def print_similar_items(self, mid: int) -> None:
        # TODO

        self.cursor.execute(
            """
            SELECT t2.TITLE, s.SIMILARITY 
            FROM ofirtam.dbo.Similarity s
            JOIN ofirtam.dbo.MediaItems t1 ON s.MID1 = t1.MID
            JOIN ofirtam.dbo.MediaItems t2 ON s.MID2 = t2.MID
            WHERE s.MID1 = ? AND s.SIMILARITY >= 0.25
            ORDER BY s.SIMILARITY ASC
            """,
            (mid,)
        )
        rows = self.cursor.fetchall()
        for row in rows:
            print(f"{row[0]} {row[1]}")


    def add_summary_items(self) -> None:
        self.cursor.execute("EXEC AddSummaryItems")
        
        self.conn.commit()