import random
import re
import pymysql
import pandas as pd


def connect_to_sql(db_name='your_database_name'):
    try:
        connection = pymysql.connect(
            host='13.57.26.234',  
            user='root',  
            password='Dsci-551',  
            database=db_name,  
            port=3306  
        )
        print("Database connection successful!")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

sql_query_patterns = [
    {
        "type": "WHERE",
        "description": lambda table: f"Retrieve all rows from the table '{table}' where a specific column is not null (with a limit of 5 rows).",
        "query": lambda table, column: f"SELECT * FROM {table} WHERE {column} IS NOT NULL LIMIT 5;"
    },
    {
        "type": "JOIN",
        "description": lambda table1, table2: f"Join the tables '{table1}' and '{table2}' on a specific column, selecting related information from both tables (with a limit of 10 rows).",
        "query": lambda table1, table2, column1, column2: f"SELECT a.{column1}, b.{column2} FROM {table1} a JOIN {table2} b ON a.{column1} = b.{column2} LIMIT 10;"
    },
    {
        "type": "HAVING",
        "description": lambda table: f"Group rows in the table '{table}' by a specific column and calculate the total sum for another column, displaying results where the sum exceeds 100.",
        "query": lambda table, column1, column2: f"SELECT {column1}, SUM({column2}) AS total_{column2} FROM {table} GROUP BY {column1} HAVING total_{column2} > 100;"
    },
    {
        "type": "ORDER BY",
        "description": lambda table: f"Retrieve all rows from the table '{table}' and sort them in descending order by a specific column (with a limit of 5 rows).",
        "query": lambda table, column: f"SELECT * FROM {table} ORDER BY {column} DESC LIMIT 5;"
    },
    {
        "type": "GROUP BY",
        "description": lambda table: f"Group rows in the table '{table}' by a specific column, count the number of rows in each group, and display the groups in descending order of count (with a limit of 5 groups).",
        "query": lambda table, column: f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} ORDER BY COUNT(*) DESC LIMIT 5;"
    }
]


def generate_sql_queries(connection):
    try:
        print("\nChoose a Query Type:")
        for i, pattern in enumerate(sql_query_patterns, 1):
            print(f"{i}. {pattern['type']}")  

        query_type = input("Enter your choice (1-5): ")

    
        if not query_type.isdigit() or not (1 <= int(query_type) <= len(sql_query_patterns)):
            print("Invalid choice. Please enter a valid number between 1 and 5.")
            return


        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if not tables:
                print("No tables available in the database.")
                return

    
            table1 = random.choice(tables)[0]
            cursor.execute(f"DESCRIBE {table1}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]

          
            query_index = int(query_type) - 1
            query_info = sql_query_patterns[query_index]

     
            description = (
                query_info["description"](table1, "table2")
                if "table2" in query_info["description"].__code__.co_varnames
                else query_info["description"](table1)
            )

        
            if "table2" in query_info["query"].__code__.co_varnames:
                if len(tables) < 2:
                    print("Not enough tables available for a JOIN query.")
                    return
                table2 = random.choice([t[0] for t in tables if t[0] != table1])
                column1 = random.choice(column_names)
                cursor.execute(f"DESCRIBE {table2}")
                columns_table2 = cursor.fetchall()
                column2 = random.choice([column[0] for column in columns_table2])
                generated_query = query_info["query"](table1, table2, column1, column2)
            elif "column2" in query_info["query"].__code__.co_varnames:
                if len(column_names) < 2:
                    print("Not enough columns available for this type of query.")
                    return
                column1, column2 = random.sample(column_names, 2)
                generated_query = query_info["query"](table1, column1, column2)
            elif "column" in query_info["query"].__code__.co_varnames:
                column = random.choice(column_names)
                generated_query = query_info["query"](table1, column)
            else:
                generated_query = query_info["query"](table1)

       
            print("\nGenerated Query:")
            print(f"Description: {description}")
            print(f"SQL Query: {generated_query}")

    except Exception as e:
        print(f"Error generating SQL queries: {e}")




nlp_to_sql_patterns = [

    {
        "pattern": r"total number of rows in the (\w+)",
        "query": lambda table: f"SELECT COUNT(*) FROM {table};"
    },

    {
        "pattern": r"all data from the (\w+)",
        "query": lambda table: f"SELECT * FROM {table} LIMIT 10;"
    },

    {
        "pattern": r"distinct values of (\w+) in the (\w+)",
        "query": lambda column, table: f"SELECT DISTINCT {column} FROM {table};"
    },

    {
        "pattern": r"average (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT AVG({column}) FROM {table};"
    },

    {
        "pattern": r"sum of (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT SUM({column}) FROM {table};"
    },

    {
        "pattern": r"find all rows in (\w+) where (\w+) is not null",
        "query": lambda table, column: f"SELECT * FROM {table} WHERE {column} IS NOT NULL LIMIT 10;"
    },

    {
        "pattern": r"minimum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MIN({column}) FROM {table};"
    },

    {
        "pattern": r"maximum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MAX({column}) FROM {table};"
    },

    {
        "pattern": r"all rows from (\w+) ordered by (.+)",
        "query": lambda table, column: f"SELECT * FROM {table} ORDER BY {column} DESC LIMIT 10;"
    },
 
    {
        "pattern": r"count number of rows grouped by (\w+) in the (\w+)",
        "query": lambda column, table: f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} ORDER BY COUNT(*) DESC LIMIT 10;"
    },

    {
        "pattern": r"sum of (.+?) grouped by (\w+) in the (\w+)",
        "query": lambda sum_column, group_column, table: f"SELECT {group_column}, SUM({sum_column}) FROM {table} GROUP BY {group_column} ORDER BY SUM({sum_column}) DESC LIMIT 10;"
    },

    {
        "pattern": r"find all rows in (\w+) where (\w+) is (.+)",
        "query": lambda table, column, value: f"SELECT * FROM {table} WHERE {column} = '{value}' LIMIT 10;"
    },
 
    {
        "pattern": r"minimum and maximum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MIN({column}) AS min_{column}, MAX({column}) AS max_{column} FROM {table};"
    },
 
    {
        "pattern": r"find all rows in (\w+) where (\w+) is greater than (.+) and (\w+) is '(.+)'",
        "query": lambda table, column1, value1, column2, value2: f"SELECT * FROM {table} WHERE {column1} > {value1} AND {column2} = '{value2}' LIMIT 10;"
    },

    {
        "pattern": r"average (.+?) grouped by (\w+) in the (\w+)",
        "query": lambda avg_column, group_column, table: f"SELECT {group_column}, AVG({avg_column}) FROM {table} GROUP BY {group_column} ORDER BY AVG({avg_column}) DESC LIMIT 10;"
    },

    {
        "pattern": r"join (\w+) and (\w+) on (\w+) = (\w+)",
        "query": lambda table1, table2, column1, column2: f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{column1} = {table2}.{column2} LIMIT 10;"
    },

    {
        "pattern": r"join (\w+) and (\w+) on (\w+) = (\w+) where (.+?) having (.+)",
        "query": lambda table1, table2, column1, column2, where_condition, having_condition: 
            f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{column1} = {table2}.{column2} WHERE {where_condition} HAVING {having_condition} LIMIT 10;"
    },

    {
        "pattern": r"group rows by (\w+) in the (\w+) having (.+)",
        "query": lambda group_column, table, having_condition: 
            f"SELECT {group_column}, COUNT(*) FROM {table} GROUP BY {group_column} HAVING {having_condition} ORDER BY COUNT(*) DESC LIMIT 10;"
    },

    {
        "pattern": r"sum of (.+?) grouped by (\w+) in the (\w+) having (.+)",
        "query": lambda sum_column, group_column, table, having_condition: 
            f"SELECT {group_column}, SUM({sum_column}) FROM {table} GROUP BY {group_column} HAVING {having_condition} ORDER BY SUM({sum_column}) DESC LIMIT 10;"
    },

    {
        "pattern": r"left join (\w+) and (\w+) on (\w+) = (\w+)",
        "query": lambda table1, table2, column1, column2: 
            f"SELECT * FROM {table1} LEFT JOIN {table2} ON {table1}.{column1} = {table2}.{column2} LIMIT 10;"
    },

    {
        "pattern": r"delete rows in (\w+) where (\w+) is (.+)",
        "query": lambda table, column, value: f"DELETE FROM {table} WHERE {column} = '{value}';"
    },
 
    {
        "pattern": r"update (\w+) set (\w+) to (.+) where (\w+) is (.+)",
        "query": lambda table, set_column, new_value, where_column, where_value: 
            f"UPDATE {table} SET {set_column} = '{new_value}' WHERE {where_column} = '{where_value}';"
    },
   
    {
        "pattern": r"find (\w+) and count from (\w+) grouped by (\w+) having (.+)",
        "query": lambda select_column, table, group_column, having_condition: 
            f"SELECT {select_column}, COUNT(*) FROM {table} GROUP BY {group_column} HAVING {having_condition} LIMIT 10;"
    },

    {
        "pattern": r"union of (.+?) from (\w+) and (.+?) from (\w+)",
        "query": lambda columns1, table1, columns2, table2: 
            f"SELECT {columns1} FROM {table1} UNION SELECT {columns2} FROM {table2};"
    }
]

def nlp_to_sql(nlp_input, connection):

    nlp_input_lower = nlp_input.lower().strip() 

    try:
        with connection.cursor() as cursor:
            
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

         
            for pattern_info in nlp_to_sql_patterns:
                match = re.search(pattern_info["pattern"], nlp_input_lower)
                if match:
                  
                    groups = match.groups()

                
                    if len(groups) == 1:
                   
                        table_name = groups[0].strip()
                    elif len(groups) == 2:
             
                        column_name, table_name = groups
                        column_name = column_name.strip()
                        table_name = table_name.strip()
                    else:
                        print("Unable to generate a query with the provided natural language input.")
                        return

             
                    table_name_original = next((table for table in tables if table.lower() == table_name.lower()), None)
                    if not table_name_original:
                        print(f"Table name '{table_name}' not found in the database.")
                        return

             
                    if 'column' in pattern_info["query"].__code__.co_varnames:
         
                        cursor.execute(f"DESCRIBE {table_name_original}")
                        columns = [column[0] for column in cursor.fetchall()]

                        column_name_original = next((col for col in columns if col.lower() == column_name.lower()), None)
                        if not column_name_original:
                            print(f"Column name '{column_name}' not found in the selected table '{table_name_original}'.")
                            return

    
                        sql_query = pattern_info["query"](column_name_original, table_name_original)
                    else:
            
                        sql_query = pattern_info["query"](table_name_original)

        
                    cursor.execute(sql_query)
                    result = cursor.fetchall()
                    print("\nGenerated SQL Query:")
                    print(f"  {sql_query}")
                    print("\nQuery Result:")
                    for row in result:
                        print(row)
                    return

            print("Unable to match the provided natural language input to a known query pattern.")

    except Exception as e:
        print(f"Error executing query: {e}")


def show_sample_sql_queries(connection):
    try:
        with connection.cursor() as cursor:
        
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                print("No tables available in the database.")
                return

            selected_queries = random.sample(sql_query_patterns, 3)  
            print("\nSample SQL Queries:")

            for query_info in selected_queries:
                table1 = random.choice(tables)[0]
                cursor.execute(f"DESCRIBE {table1}")
                columns = cursor.fetchall()
                column_names = [column[0] for column in columns]

            
                if 'table2' in query_info["query"].__code__.co_varnames:
                    if len(tables) < 2:
                        print("Not enough tables available for a JOIN query.")
                        continue  

              
                    table2 = random.choice([t[0] for t in tables if t[0] != table1])

             
                    cursor.execute(f"DESCRIBE {table2}")
                    columns_table2 = cursor.fetchall()
                    column1 = random.choice(column_names)
                    column2 = random.choice([column[0] for column in columns_table2])

         
                    generated_description = query_info["description"](table1, table2)
                    generated_query = query_info["query"](table1, table2, column1, column2)

                elif 'column2' in query_info["query"].__code__.co_varnames:
                    if len(column_names) < 2:
                        print("Not enough columns available for this type of query.")
                        continue  
                    column1, column2 = random.sample(column_names, 2)
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1, column1, column2)
        
                elif 'column' in query_info["query"].__code__.co_varnames:
                    column = random.choice(column_names)
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1, column)
    
                else:
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1)

   
                print(f"- Description: {generated_description}")
                print(f"  Query: {generated_query}")

    except Exception as e:
        print(f"Error generating sample SQL queries: {e}")

def upload_data_to_sql(connection, csv_file_path, table_name):

    try:
 
        data = pd.read_csv(csv_file_path)

        if data.empty:
            print("The provided CSV file is empty.")
            return

        with connection.cursor() as cursor:
 
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()

      
            if not table_exists:
                columns = ", ".join([f"{col} VARCHAR(255)" for col in data.columns])
                create_table_query = f"CREATE TABLE {table_name} ({columns})"
                cursor.execute(create_table_query)
                print(f"Table '{table_name}' created successfully.")

     
            for _, row in data.iterrows():
                placeholders = ', '.join(['%s'] * len(row))
                insert_query = f"INSERT INTO {table_name} ({', '.join(row.index)}) VALUES ({placeholders})"
                cursor.execute(insert_query, tuple(row))
            
     
            connection.commit()
            print(f"Data from '{csv_file_path}' uploaded successfully to table '{table_name}'.")

    except Exception as e:
        print(f"Error uploading data to SQL database: {e}")


def show_database_structure(connection):

    try:
        with connection.cursor() as cursor:

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                print("No tables available in the database.")
                return

            print("\nDatabase Structure and Sample Data:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")

     
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for column in columns:
                    column_name = column[0]
                    data_type = column[1]
                    print(f"  - Column: {column_name}, Type: {data_type}")

     
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()

                if sample_data:
                    print(f"\n  Sample Data from {table_name}:")

                    column_headers = [column[0] for column in columns]
                    print(f"  {column_headers}")

                    for row in sample_data:
                        print(f"  {row}")
                else:
                    print(f"  No sample data available for table '{table_name}'.")

    except Exception as e:
        print(f"Error fetching database structure and sample data: {e}")

def execute_user_query(connection, user_query):

    try:
        with connection.cursor() as cursor:

            cursor.execute(user_query)
            results = cursor.fetchall()


            if results:
                print("\nQuery Results:")
                for row in results:
                    print(row)
            else:
                print("\nNo results found or query executed successfully.")


            if user_query.strip().lower().startswith(("insert", "update", "delete")):
                connection.commit()
                print("Changes committed to the database.")

    except Exception as e:
        print(f"Error executing user query: {e}")
