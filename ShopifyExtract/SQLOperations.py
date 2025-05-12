# Mostly not useful, as we will use pandas sql to insert the data into SQL Server.

import pandas as pd
import pyodbc

def insert_into_sql_server(query: str, dataframe: pd.DataFrame, connection_string: str):
    """
    Inserts data from a pandas DataFrame into a SQL Server table using the provided query.

    Parameters:
        query (str): The SQL INSERT query with placeholders for the values.
        dataframe (pd.DataFrame): The DataFrame containing the data to be inserted.
        connection_string (str): The connection string for the SQL Server database.

    Example:
        query = "INSERT INTO TableName (Column1, Column2) VALUES (?, ?)"
        insert_into_sql_server(query, df, connection_string)
    """
    try:
        # Establish connection to SQL Server
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # Iterate through the DataFrame rows and execute the query
            for index, row in dataframe.iterrows():
                cursor.execute(query, tuple(row))
            
            # Commit the transaction
            conn.commit()
            print("Data inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")