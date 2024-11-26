from pymongo import MongoClient
import random
import json
import re
import pymysql
import pandas as pd

def connect_to_mongo():
    client = MongoClient(
        host='13.57.241.139',  # Replace with your EC2 public IP address
        port=27017  # MongoDB default port
    )
    db = client['orders']  # Replace with your MongoDB database name
    return db

def welcome_message():
    print(r"""
      ___           ___           ___           ___                    ___           ___     
     /\  \         /\__\         /\  \         /\  \                  /\  \         /\  \    
    /::\  \       /:/  /        /::\  \        \:\  \                /::\  \       /::\  \   
   /:/\:\  \     /:/__/        /:/\:\  \        \:\  \              /:/\:\  \     /:/\:\  \  
  /:/  \:\  \   /::\  \ ___   /::\~\:\  \       /::\  \            /:/  \:\__\   /::\~\:\__\ 
 /:/__/ \:\__\ /:/\:\  /\__\ /:/\:\ \:\__\     /:/\:\__\          /:/__/ \:|__| /:/\:\ \:|__|
 \:\  \  \/__/ \/__\:\/:/  / \/__\:\/:/  /    /:/  \/__/          \:\  \ /:/  / \:\~\:\/:/  /
  \:\  \            \::/  /       \::/  /    /:/  /                \:\  /:/  /   \:\ \::/  / 
   \:\  \           /:/  /        /:/  /     \/__/                  \:\/:/  /     \:\/:/  /  
    \:\__\         /:/  /        /:/  /                              \::/__/       \::/__/   
     \/__/         \/__/         \/__/                                ~~            ~~       

  ___  ____   __   _  _  ____     ___  ___  
 / __)(  _ \ /  \ / )( \(  _ \   / __)/ _ \ 
( (_ \ )   /(  O )) \/ ( ) __/  (  _ \\__  )
 \___/(__\_) \__/ \____/(__)     \___/(___/ 


       Welcome to ChatDB!
    
    ---------------------------------------
    Developed by: Tengjiang Wang Zifeng Zhou
    ---------------------------------------
    
    Please choose a database:
    1. SQL Database
    2. MongoDB Database
    """)

def exit_message():
    print(r'''
                                                                                              
8888888 8888888888 8 8888        8          .8.          b.             8 8 8888     ,88' 
      8 8888       8 8888        8         .888.         888o.          8 8 8888    ,88'  
      8 8888       8 8888        8        :88888.        Y88888o.       8 8 8888   ,88'   
      8 8888       8 8888        8       . `88888.       .`Y888888o.    8 8 8888  ,88'    
      8 8888       8 8888        8      .8. `88888.      8o. `Y888888o. 8 8 8888 ,88'     
      8 8888       8 8888        8     .8`8. `88888.     8`Y8o. `Y88888o8 8 8888 88'      
      8 8888       8 8888888888888    .8' `8. `88888.    8   `Y8o. `Y8888 8 888888<       
      8 8888       8 8888        8   .8'   `8. `88888.   8      `Y8o. `Y8 8 8888 `Y8.     
      8 8888       8 8888        8  .888888888. `88888.  8         `Y8o.` 8 8888   `Y8.   
      8 8888       8 8888        8 .8'       `8. `88888. 8            `Yo 8 8888     `Y8. 
                                                  
`8.`8888.      ,8'  ,o888888o.     8 8888      88 
 `8.`8888.    ,8'. 8888     `88.   8 8888      88 
  `8.`8888.  ,8',8 8888       `8b  8 8888      88 
   `8.`8888.,8' 88 8888        `8b 8 8888      88 
    `8.`88888'  88 8888         88 8 8888      88 
     `8. 8888   88 8888         88 8 8888      88 
      `8 8888   88 8888        ,8P 8 8888      88 
       8 8888   `8 8888       ,8P  ` 8888     ,8P 
       8 8888    ` 8888     ,88'     8888   ,d8P  
       8 8888       `8888888P'        `Y88888P'    ''')

def explore_database(db):
    collections = db.list_collection_names()
    collections_info = {}

    for collection_name in collections:
        collection = db[collection_name]
        sample_data = collection.find_one()  # Get one document as a sample
        if sample_data:
            fields = sample_data.keys()
            collections_info[collection_name] = {
                "fields": list(fields),
                "sample_data": sample_data
            }
        else:
            collections_info[collection_name] = {
                "fields": [],
                "sample_data": "No data available"
            }

    for collection, info in collections_info.items():
        print(f"\nCollection: {collection}")
        print(f"Fields: {info['fields']}")
        print(f"Sample Data: {info['sample_data']}")

query_patterns = [
    {
        "description": "Find all documents in the collection.",
        "query": lambda collection: f"db.{collection}.find({{}})"
    },
    {
        "description": "Retrieve unique values of a field (Distinct).",
        "query": lambda collection, field: f"db.{collection}.distinct('{field}')"
    },
    {
        "description": "Sort documents by a specific field.",
        "query": lambda collection, field: f"db.{collection}.find().sort({{{field}: -1}})"
    },
    {
        "description": "Group by a field and count documents.",
        "query": lambda collection, field: f"db.{collection}.aggregate([{{'$group': {{'_id': '${field}', 'count': {{'$sum': 1}}}}}}])"
    },
    {
        "description": "Filter and return specific fields (Projection).",
        "query": lambda collection, field: f"db.{collection}.find({{}}, {{'{field}': 1, '_id': 0}})"
    }
]

# 选项 2：展示 3 个样本查询
def show_sample_queries(db):
    collections = db.list_collection_names()

    if not collections:
        print("No collections available in the database.")
        return

    selected_queries = random.sample(query_patterns, 3)  # 随机选择3个查询模式
    print("\nSample Queries:")

    for query_info in selected_queries:
        collection = random.choice(collections)
        sample_data = db[collection].find_one()

        if sample_data:
            fields = list(sample_data.keys())

            if 'field2' in query_info["query"].__code__.co_varnames:
                # 确保至少有两个字段供多条件过滤
                if len(fields) >= 2:
                    field1, field2 = random.sample(fields, 2)
                    print(f"- Description: {query_info['description']}")
                    print(f"  Query: {query_info['query'](collection, field1, field2)}")
            else:
                if 'field' in query_info["query"].__code__.co_varnames:
                    field = random.choice(fields)
                    print(f"- Description: {query_info['description']}")
                    print(f"  Query: {query_info['query'](collection, field)}")
                else:
                    print(f"- Description: {query_info['description']}")
                    print(f"  Query: {query_info['query'](collection)}")

# 选项 3：生成查询（用户选择查询类型）
def generate_queries(db):
    print("\nChoose a Query Type:")
    for i, pattern in enumerate(query_patterns, 1):
        print(f"{i}. {pattern['description']}")
    query_type = input("Enter your choice (1-5): ")

    if not query_type.isdigit() or not (1 <= int(query_type) <= len(query_patterns)):
        print("Invalid choice. Please enter a valid number between 1 and 5.")
        return

    collections = db.list_collection_names()
    collection = random.choice(collections)
    sample_data = db[collection].find_one()

    if sample_data:
        fields = list(sample_data.keys())
    else:
        print("No data available in the chosen collection.")
        return

    query_index = int(query_type) - 1
    query_info = query_patterns[query_index]

    # 根据选择的查询类型生成查询
    if 'field2' in query_info["query"].__code__.co_varnames and len(fields) >= 2:
        field1, field2 = random.sample(fields, 2)
        generated_query = query_info["query"](collection, field1, field2)
    elif 'field' in query_info["query"].__code__.co_varnames:
        field = random.choice(fields)
        generated_query = query_info["query"](collection, field)
    else:
        generated_query = query_info["query"](collection)

    print("\nGenerated Query:")
    print(f"  {generated_query}")

# 自然语言查询解析函数
def parse_query(query):
    # 将查询转换为小写，便于匹配
    query = query.lower()

    # 定义集合和对应的操作类型
    collections = ['products', 'orders', 'reviews', 'categories', 'users']
    actions = {
        'find': ['find', 'list', 'show'],
        'count': ['count', 'how many'],
        'sort': ['sort', 'order by'],
        'group': ['group by', 'aggregate'],
        'distinct': ['distinct', 'unique', 'different'],
        'project': ['only', 'show', 'display']
    }

    # 查找目标集合
    collection = None
    for col in collections:
        if col in query:
            collection = col
            break

    # 查找操作
    action = None
    for key, keywords in actions.items():
        for keyword in keywords:
            if keyword in query:
                action = key
                break

    if collection and action:
        return action, collection
    else:
        return None, None

# NLP 查询生成函数
def generate_nlp_query(query):
    action, collection = parse_query(query)

    if not action or not collection:
        return {"error": "Could not determine action or target collection from the input."}

    # 根据 action 和 collection 生成查询
    if action == 'find':
        mongo_query = f"db.{collection}.find({{}}).limit(10)"
    elif action == 'count':
        mongo_query = f"db.{collection}.countDocuments({{}})"
    elif action == 'sort':
        mongo_query = f"db.{collection}.find({{}}).sort({{ 'field': 1 }}).limit(10)"
    elif action == 'group':
        mongo_query = f"db.{collection}.aggregate([{{ '$group': {{ '_id': '$field', 'count': {{ '$sum': 1 }} }} }}])"
    elif action == 'distinct':
        mongo_query = f"db.{collection}.distinct('field')"
    elif action == 'project':
        mongo_query = f"db.{collection}.find({{}}, {{ 'field': 1, '_id': 0 }})"
    else:
        mongo_query = {"error": "Unknown action."}

    return mongo_query

# 选项 4：NLP 示例
def nlp_examples():
    print("\nNLP Examples:")
    print("- Find all documents in the collection")
    print("- Retrieve unique values of a field (e.g., 'Find distinct product categories')")
    print("- Sort orders by order date")
    print("- Group customers by region and count them")
    print("- Show only product names and prices in the collection")
    user_query = input("Enter your query: ")
    mongo_query = generate_nlp_query(user_query)
    print(f"Generated Query: {mongo_query}")

# option 5
def upload_json_to_mongodb(db):
    # 提示用户输入文件路径
    file_path = input("Enter the file path to upload (JSON format): ")

    # 提示用户输入集合名称
    collection_name = input("Enter the target collection name in MongoDB: ")

    collection = db[collection_name]

    try:
        # 打开 JSON 文件并读取数据
        with open(file_path, 'r') as file:
            data = json.load(file)

            if isinstance(data, list):
                collection.insert_many(data)
                print(f"Successfully uploaded {len(data)} records to the '{collection_name}' collection.")
            elif isinstance(data, dict):
                collection.insert_one(data)
                print(f"Successfully uploaded 1 record to the '{collection_name}' collection.")
            else:
                print("Unsupported JSON format.")

    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")
    except Exception as e:
        print(f"Error uploading data: {e}")

def test_query(db):
    print("\nEnter your MongoDB query (e.g., db.collection.find()):")
    user_query = input("Query: ")

    try:
        # 匹配集合名和操作类型
        collection_match = re.match(r"db\.([a-zA-Z_]+)\.([a-zA-Z_]+)\((.*)\)", user_query)
        if not collection_match:
            print("Invalid query format. Please use the format: db.collection.operation()")
            return

        collection_name = collection_match.group(1)
        operation = collection_match.group(2)
        parameters = collection_match.group(3).strip()

        collection = db[collection_name]

        # 处理 find 操作
        if operation == "find":
            if parameters:
                filter_dict = eval(parameters)  # 将字符串转换为字典（注意安全性）
                result = collection.find(filter_dict)
            else:
                result = collection.find()
            for doc in result:
                print(doc)

        # 处理 count_documents 操作
        elif operation == "count":
            if parameters:
                filter_dict = eval(parameters)
                count = collection.count_documents(filter_dict)
            else:
                count = collection.count_documents({})
            print(f"Count: {count}")

        # 处理 aggregate 操作（分组）
        elif operation == "aggregate":
            if parameters:
                pipeline = eval(parameters)  # 将字符串转换为列表（注意安全性）
            else:
                pipeline = []
            result = collection.aggregate(pipeline)
            for doc in result:
                print(doc)

        # 处理 sort 操作
        elif operation == "sort":
            if parameters:
                sort_field, sort_order = parameters.split(",")
                sort_field = sort_field.strip()
                sort_order = int(sort_order.strip())
                result = collection.find().sort(sort_field, sort_order)
                for doc in result:
                    print(doc)
            else:
                print("Sort operation requires field and order (e.g., 'field, 1' or 'field, -1')")

        # 处理其他不支持的操作
        else:
            print("Unsupported operation. Supported operations: find, count, aggregate, sort")

    except Exception as e:
        print(f"Error executing query: {e}")


#############################################################SQL#####################################################################

# 选项 1：建立数据库连接
def connect_to_sql(db_name='your_database_name'):
    """
    Connects to an SQL database and returns the connection object.

    Parameters:
    db_name (str): The name of the database to connect to.

    Returns:
    connection: The connection object for the SQL database.
    """
    try:
        connection = pymysql.connect(
            host='13.57.26.234',  # Replace with your database host address
            user='root',  # Replace with your database username
            password='Dsci-551',  # Replace with your database password
            database=db_name,  # The database to connect to
            port=3306  # Database port (default for MySQL is 3306)
        )
        print("Database connection successful!")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# 定义 SQL 查询模式
sql_query_patterns = [
    {
        "description": lambda table: f"Retrieve all rows from the table '{table}' where a specific column is not null (with a limit of 5 rows)",
        "query": lambda table, column: f"SELECT * FROM {table} WHERE {column} IS NOT NULL LIMIT 5;"
    },
    {
        "description": lambda table1, table2: f"Join the tables '{table1}' and '{table2}' on a specific column, selecting related information from both tables (with a limit of 10 rows)",
        "query": lambda table1, table2, column1, column2: f"SELECT a.{column1}, b.{column2} FROM {table1} a JOIN {table2} b ON a.{column1} = b.{column2} LIMIT 10;"
    },
    {
        "description": lambda table: f"Group rows in the table '{table}' by a specific column and calculate the total sum for another column, displaying results where the sum exceeds 100",
        "query": lambda table, column1, column2: f"SELECT {column1}, SUM({column2}) AS total_{column2} FROM {table} GROUP BY {column1} HAVING total_{column2} > 100;"
    },
    {
        "description": lambda table: f"Retrieve all rows from the table '{table}' and sort them in descending order by a specific column (with a limit of 5 rows)",
        "query": lambda table, column: f"SELECT * FROM {table} ORDER BY {column} DESC LIMIT 5;"
    },
    {
        "description": lambda table: f"Group rows in the table '{table}' by a specific column, count the number of rows in each group, and display the groups in descending order of count (with a limit of 5 groups)",
        "query": lambda table, column: f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} ORDER BY COUNT(*) DESC LIMIT 5;"
    }
]


# 让用户选择查询类型并生成对应的SQL查询
def generate_sql_queries(connection):
    try:
        # 打印查询类型供用户选择
        print("\nChoose a Query Type:")
        for i, pattern in enumerate(sql_query_patterns, 1):
            print(f"{i}. {pattern['description']}")
        query_type = input("Enter your choice (1-5): ")

        # 验证用户输入是否有效
        if not query_type.isdigit() or not (1 <= int(query_type) <= len(sql_query_patterns)):
            print("Invalid choice. Please enter a valid number between 1 and 5.")
            return

        # 获取所有表格名称
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if not tables:
                print("No tables available in the database.")
                return

            # 随机选择表格以生成查询
            table1 = random.choice(tables)[0]
            cursor.execute(f"DESCRIBE {table1}")
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]

            # 根据选择的查询类型生成查询
            query_index = int(query_type) - 1
            query_info = sql_query_patterns[query_index]

            # 如果是JOIN查询，随机选择两个表格和对应列
            if 'table2' in query_info["query"].__code__.co_varnames:
                if len(tables) < 2:
                    print("Not enough tables available for a JOIN query.")
                    return
                table2 = random.choice([t[0] for t in tables if t[0] != table1])
                column1 = random.choice(column_names)
                cursor.execute(f"DESCRIBE {table2}")
                columns_table2 = cursor.fetchall()
                column2 = random.choice([column[0] for column in columns_table2])
                generated_query = query_info["query"](table1, table2, column1, column2)
            # 如果需要两个列
            elif 'column2' in query_info["query"].__code__.co_varnames:
                if len(column_names) < 2:
                    print("Not enough columns available for this type of query.")
                    return
                column1, column2 = random.sample(column_names, 2)
                generated_query = query_info["query"](table1, column1, column2)
            # 如果只需要一个列
            elif 'column' in query_info["query"].__code__.co_varnames:
                column = random.choice(column_names)
                generated_query = query_info["query"](table1, column)
            # 不需要特定列
            else:
                generated_query = query_info["query"](table1)

            # 输出生成的查询
            print("\nGenerated Query:")
            print(f"  {generated_query}")

    except Exception as e:
        print(f"Error generating SQL queries: {e}")

nlp_to_sql_patterns = [
    # 行数统计
    {
        "pattern": r"total number of rows in the (\w+)",
        "query": lambda table: f"SELECT COUNT(*) FROM {table};"
    },
    # 获取所有数据
    {
        "pattern": r"all data from the (\w+)",
        "query": lambda table: f"SELECT * FROM {table} LIMIT 10;"
    },
    # 获取唯一值
    {
        "pattern": r"distinct values of (\w+) in the (\w+)",
        "query": lambda column, table: f"SELECT DISTINCT {column} FROM {table};"
    },
    # 计算平均值
    {
        "pattern": r"average (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT AVG({column}) FROM {table};"
    },
    # 计算总和
    {
        "pattern": r"sum of (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT SUM({column}) FROM {table};"
    },
    # 查找列不为空的所有行
    {
        "pattern": r"find all rows in (\w+) where (\w+) is not null",
        "query": lambda table, column: f"SELECT * FROM {table} WHERE {column} IS NOT NULL LIMIT 10;"
    },
    # 查找某列的最小值
    {
        "pattern": r"minimum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MIN({column}) FROM {table};"
    },
    # 查找某列的最大值
    {
        "pattern": r"maximum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MAX({column}) FROM {table};"
    },
    # 按某列排序数据
    {
        "pattern": r"all rows from (\w+) ordered by (.+)",
        "query": lambda table, column: f"SELECT * FROM {table} ORDER BY {column} DESC LIMIT 10;"
    },
    # 按某列分组并统计数量
    {
        "pattern": r"count number of rows grouped by (\w+) in the (\w+)",
        "query": lambda column, table: f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} ORDER BY COUNT(*) DESC LIMIT 10;"
    },
    # 按某列分组并计算总和
    {
        "pattern": r"sum of (.+?) grouped by (\w+) in the (\w+)",
        "query": lambda sum_column, group_column, table: f"SELECT {group_column}, SUM({sum_column}) FROM {table} GROUP BY {group_column} ORDER BY SUM({sum_column}) DESC LIMIT 10;"
    },
    # 查找特定值的所有行
    {
        "pattern": r"find all rows in (\w+) where (\w+) is (.+)",
        "query": lambda table, column, value: f"SELECT * FROM {table} WHERE {column} = '{value}' LIMIT 10;"
    },
    # 查找某列的最小值和最大值
    {
        "pattern": r"minimum and maximum (.+?) in the (\w+)",
        "query": lambda column, table: f"SELECT MIN({column}) AS min_{column}, MAX({column}) AS max_{column} FROM {table};"
    },
    # 多条件过滤
    {
        "pattern": r"find all rows in (\w+) where (\w+) is greater than (.+) and (\w+) is '(.+)'",
        "query": lambda table, column1, value1, column2, value2: f"SELECT * FROM {table} WHERE {column1} > {value1} AND {column2} = '{value2}' LIMIT 10;"
    },
    # 计算某列的平均值并按另一列分组
    {
        "pattern": r"average (.+?) grouped by (\w+) in the (\w+)",
        "query": lambda avg_column, group_column, table: f"SELECT {group_column}, AVG({avg_column}) FROM {table} GROUP BY {group_column} ORDER BY AVG({avg_column}) DESC LIMIT 10;"
    },
    # 连接两个表
    {
        "pattern": r"join (\w+) and (\w+) on (\w+) = (\w+)",
        "query": lambda table1, table2, column1, column2: f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{column1} = {table2}.{column2} LIMIT 10;"
    },
    # 连接两个表并使用HAVING筛选
    {
        "pattern": r"join (\w+) and (\w+) on (\w+) = (\w+) where (.+?) having (.+)",
        "query": lambda table1, table2, column1, column2, where_condition, having_condition: 
            f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{column1} = {table2}.{column2} WHERE {where_condition} HAVING {having_condition} LIMIT 10;"
    },
    # 按某列分组并使用HAVING过滤
    {
        "pattern": r"group rows by (\w+) in the (\w+) having (.+)",
        "query": lambda group_column, table, having_condition: 
            f"SELECT {group_column}, COUNT(*) FROM {table} GROUP BY {group_column} HAVING {having_condition} ORDER BY COUNT(*) DESC LIMIT 10;"
    },
    # 计算总和并按某列分组，使用HAVING过滤
    {
        "pattern": r"sum of (.+?) grouped by (\w+) in the (\w+) having (.+)",
        "query": lambda sum_column, group_column, table, having_condition: 
            f"SELECT {group_column}, SUM({sum_column}) FROM {table} GROUP BY {group_column} HAVING {having_condition} ORDER BY SUM({sum_column}) DESC LIMIT 10;"
    },
    # 左连接两个表
    {
        "pattern": r"left join (\w+) and (\w+) on (\w+) = (\w+)",
        "query": lambda table1, table2, column1, column2: 
            f"SELECT * FROM {table1} LEFT JOIN {table2} ON {table1}.{column1} = {table2}.{column2} LIMIT 10;"
    },
    # 删除表中满足特定条件的行
    {
        "pattern": r"delete rows in (\w+) where (\w+) is (.+)",
        "query": lambda table, column, value: f"DELETE FROM {table} WHERE {column} = '{value}';"
    },
    # 更新表中特定条件的行
    {
        "pattern": r"update (\w+) set (\w+) to (.+) where (\w+) is (.+)",
        "query": lambda table, set_column, new_value, where_column, where_value: 
            f"UPDATE {table} SET {set_column} = '{new_value}' WHERE {where_column} = '{where_value}';"
    },
    # 使用聚合函数并且使用HAVING筛选
    {
        "pattern": r"find (\w+) and count from (\w+) grouped by (\w+) having (.+)",
        "query": lambda select_column, table, group_column, having_condition: 
            f"SELECT {select_column}, COUNT(*) FROM {table} GROUP BY {group_column} HAVING {having_condition} LIMIT 10;"
    },
    # 联合两个查询
    {
        "pattern": r"union of (.+?) from (\w+) and (.+?) from (\w+)",
        "query": lambda columns1, table1, columns2, table2: 
            f"SELECT {columns1} FROM {table1} UNION SELECT {columns2} FROM {table2};"
    }
]

def nlp_to_sql(nlp_input, connection):
    """
    将自然语言输入转换为SQL查询，并在数据库中执行查询。

    Parameters:
    nlp_input (str): 用户输入的自然语言查询描述。
    connection: SQL数据库连接对象。
    """
    nlp_input_lower = nlp_input.lower().strip()  # 用于匹配的输入全部转小写

    try:
        with connection.cursor() as cursor:
            # 获取所有表格名称（保留原始大小写）
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

            # 基于扩展的模板匹配自然语言输入
            for pattern_info in nlp_to_sql_patterns:
                match = re.search(pattern_info["pattern"], nlp_input_lower)
                if match:
                    # 匹配到自然语言的模板，获取所有匹配的组
                    groups = match.groups()

                    # 提取表名和列名，同时进行大小写匹配
                    if len(groups) == 1:
                        # 只有表格名的查询，例如行数统计
                        table_name = groups[0].strip()
                    elif len(groups) == 2:
                        # 表名和列名的查询，例如获取某列的平均值
                        column_name, table_name = groups
                        column_name = column_name.strip()
                        table_name = table_name.strip()
                    else:
                        print("Unable to generate a query with the provided natural language input.")
                        return

                    # 检查表名是否存在（不区分大小写匹配）
                    table_name_original = next((table for table in tables if table.lower() == table_name.lower()), None)
                    if not table_name_original:
                        print(f"Table name '{table_name}' not found in the database.")
                        return

                    # 如果需要列名
                    if 'column' in pattern_info["query"].__code__.co_varnames:
                        # 检查列名是否存在
                        cursor.execute(f"DESCRIBE {table_name_original}")
                        columns = [column[0] for column in cursor.fetchall()]

                        column_name_original = next((col for col in columns if col.lower() == column_name.lower()), None)
                        if not column_name_original:
                            print(f"Column name '{column_name}' not found in the selected table '{table_name_original}'.")
                            return

                        # 生成SQL查询
                        sql_query = pattern_info["query"](column_name_original, table_name_original)
                    else:
                        # 生成SQL查询（仅需要表格名称）
                        sql_query = pattern_info["query"](table_name_original)

                    # 执行SQL查询并输出结果
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

# 选项：展示3个SQL样本查询
def show_sample_sql_queries(connection):
    try:
        with connection.cursor() as cursor:
            # 获取所有表格名称
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                print("No tables available in the database.")
                return

            selected_queries = random.sample(sql_query_patterns, 3)  # 随机选择3个查询模式
            print("\nSample SQL Queries:")

            for query_info in selected_queries:
                table1 = random.choice(tables)[0]
                cursor.execute(f"DESCRIBE {table1}")
                columns = cursor.fetchall()
                column_names = [column[0] for column in columns]

                # 如果是JOIN查询，确保选择两个表格和对应的列
                if 'table2' in query_info["query"].__code__.co_varnames:
                    if len(tables) < 2:
                        print("Not enough tables available for a JOIN query.")
                        continue  # 跳过生成JOIN查询

                    # 随机选择两个不同的表格
                    table2 = random.choice([t[0] for t in tables if t[0] != table1])

                    # 获取两个表格的列信息
                    cursor.execute(f"DESCRIBE {table2}")
                    columns_table2 = cursor.fetchall()
                    column1 = random.choice(column_names)
                    column2 = random.choice([column[0] for column in columns_table2])

                    # 生成描述和SQL查询
                    generated_description = query_info["description"](table1, table2)
                    generated_query = query_info["query"](table1, table2, column1, column2)
                # 如果需要两个列
                elif 'column2' in query_info["query"].__code__.co_varnames:
                    if len(column_names) < 2:
                        print("Not enough columns available for this type of query.")
                        continue  # 跳过生成这种类型的查询
                    column1, column2 = random.sample(column_names, 2)
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1, column1, column2)
                # 如果只需要一个列
                elif 'column' in query_info["query"].__code__.co_varnames:
                    column = random.choice(column_names)
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1, column)
                # 不需要特定列
                else:
                    generated_description = query_info["description"](table1)
                    generated_query = query_info["query"](table1)

                # 输出生成的描述和查询
                print(f"- Description: {generated_description}")
                print(f"  Query: {generated_query}")

    except Exception as e:
        print(f"Error generating sample SQL queries: {e}")

def upload_data_to_sql(connection, csv_file_path, table_name):
    """
    上传 CSV 文件中的数据到 SQL 数据库。

    Parameters:
    connection: SQL数据库连接对象。
    csv_file_path (str): CSV 文件的路径。
    table_name (str): 上传数据的目标表格名称。

    """
    try:
        # 读取CSV文件数据
        data = pd.read_csv(csv_file_path)

        if data.empty:
            print("The provided CSV file is empty.")
            return

        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()

            # 如果表格不存在，创建新表
            if not table_exists:
                columns = ", ".join([f"{col} VARCHAR(255)" for col in data.columns])
                create_table_query = f"CREATE TABLE {table_name} ({columns})"
                cursor.execute(create_table_query)
                print(f"Table '{table_name}' created successfully.")

            # 插入数据到表格中
            for _, row in data.iterrows():
                placeholders = ', '.join(['%s'] * len(row))
                insert_query = f"INSERT INTO {table_name} ({', '.join(row.index)}) VALUES ({placeholders})"
                cursor.execute(insert_query, tuple(row))
            
            # 提交更改
            connection.commit()
            print(f"Data from '{csv_file_path}' uploaded successfully to table '{table_name}'.")

    except Exception as e:
        print(f"Error uploading data to SQL database: {e}")


def show_database_structure(connection):
    """
    显示数据库中所有表格及其列名称和数据类型，并展示部分示例数据。

    Parameters:
    connection: SQL数据库连接对象。
    """
    try:
        with connection.cursor() as cursor:
            # 获取所有表格名称
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                print("No tables available in the database.")
                return

            print("\nDatabase Structure and Sample Data:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")

                # 获取该表格的列名称和数据类型
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for column in columns:
                    column_name = column[0]
                    data_type = column[1]
                    print(f"  - Column: {column_name}, Type: {data_type}")

                # 获取该表格的部分示例数据
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()

                if sample_data:
                    print(f"\n  Sample Data from {table_name}:")
                    # 打印表头
                    column_headers = [column[0] for column in columns]
                    print(f"  {column_headers}")
                    # 打印数据
                    for row in sample_data:
                        print(f"  {row}")
                else:
                    print(f"  No sample data available for table '{table_name}'.")

    except Exception as e:
        print(f"Error fetching database structure and sample data: {e}")

def execute_user_query(connection, user_query):
    """
    执行用户输入的SQL查询并返回查询结果。

    Parameters:
    connection: SQL数据库连接对象。
    user_query (str): 用户输入的SQL查询语句。
    """
    try:
        with connection.cursor() as cursor:
            # 执行用户输入的SQL查询
            cursor.execute(user_query)
            results = cursor.fetchall()

            # 如果有返回结果，则打印出来
            if results:
                print("\nQuery Results:")
                for row in results:
                    print(row)
            else:
                print("\nNo results found or query executed successfully.")

            # 提交更改（对于INSERT、UPDATE、DELETE等操作）
            if user_query.strip().lower().startswith(("insert", "update", "delete")):
                connection.commit()
                print("Changes committed to the database.")

    except Exception as e:
        print(f"Error executing user query: {e}")

if __name__ == "__main__":
    while True:
        welcome_message()
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == "1":
            connection = connect_to_sql('project_db')
            while True:
                print("\nPlease choose a functionality:")
                print("1. Explore Database Collections")
                print("2. Show 3 Sample Queries")
                print("3. Generate a Query (Language Construct)")
                print("4. Enter NLP Query Example")
                print("5. Upload Data (Functionality under development)")
                print("6. Test MYSQL Query")
                print("7. Go Back to Welcome Message")
                print("8. Exit")
                sql_choice = input("Enter your choice (1-8): ")

                if sql_choice == "1":
                    show_database_structure(connection)
                elif sql_choice == "2":
                    show_sample_sql_queries(connection)
                elif sql_choice == "3":
                    generate_sql_queries(connection)
                elif sql_choice == "4":
                    print("\nEnter your natural language query (type 'QUIT' to go back to the menu):")
                    while True:
                        nlp_input = input("Enter your natural language query: ")
                        if nlp_input.strip().upper() == 'QUIT':
                            break
                        nlp_to_sql(nlp_input, connection)
                elif sql_choice == "5":
                    csv_file_path = input("Enter the path to your CSV file: ")
                    table_name = input("Enter the table name to upload data into: ")
                    upload_data_to_sql(connection, csv_file_path, table_name)
                elif sql_choice == "6":
                    print("\nEnter your SQL query (type 'QUIT' to go back to the menu):")
                    while True:
                        user_query = input("Enter your SQL query: ")
                        if user_query.strip().upper() == 'QUIT':
                            break
                        execute_user_query(connection, user_query)
                elif sql_choice == "7":
                    break
                elif sql_choice == "8":
                    exit_message()
                    exit()
                else:
                    print("Invalid choice. Please enter a valid option.")

        elif choice == "2":
            try:
                db = connect_to_mongo()  # Connect to MongoDB only when chosen
                chosen_db = "MongoDB"
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                continue

            while True:
                print("\nPlease choose a functionality:")
                print("1. Explore Database Collections")
                print("2. Show 3 Sample Queries")
                print("3. Generate a Query (Language Construct)")
                print("4. Enter NLP Query Example")
                print("5. Upload Data (Functionality under development)")
                print("6. Test MongoDB Query")
                print("7. Go Back to Welcome Message")
                print("8. Exit")
                sub_choice = input("Enter your choice: ")

                if sub_choice == "1":
                    explore_database(db)
                elif sub_choice == "2":
                    show_sample_queries(db)
                elif sub_choice == "3":
                    generate_queries(db)
                elif sub_choice == "4":
                    nlp_examples()
                elif sub_choice == "5":
                    upload_json_to_mongodb(db)
                elif sub_choice == "6":
                    test_query(db)
                elif sub_choice == "7":
                    break
                elif sub_choice == "8":
                    exit_message()
                    exit()
                else:
                    print("Invalid choice. Please enter a valid option.")
        elif choice == "3":
            exit_message()
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
            continue