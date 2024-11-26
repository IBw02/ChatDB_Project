import os
import csv
import pymysql 
from flask import Flask, render_template, request, jsonify, Response
from bson import json_util
import pandas as pd
import random
from pymongo import MongoClient

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"  # 上传文件存储目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def connect_to_sql(db_name='project_db'):
    try:
        connection = pymysql.connect(
            host='54.219.52.231',  # 数据库主机
            user='root',  # 数据库用户名
            password='Dsci-551',  # 数据库密码
            database=db_name,  # 动态选择数据库
            port=3306  # 数据库端口
        )
        print("Database connection successful!")  # 调试信息
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")  # 调试信息
        raise

def execute_sql_query(query):
    """
    执行 SQL 查询并返回结果
    """
    connection = connect_to_sql()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            # 获取列名
            columns = [desc[0] for desc in cursor.description]
            # 转换为字典列表
            result = [dict(zip(columns, row)) for row in rows]
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        connection.close()

def create_table_from_csv(cursor, table_name, data):
    """
    根据 CSV 数据动态创建新表
    """
    columns = ", ".join([f"{col} VARCHAR(255)" for col in data.columns])  # 默认所有字段类型为 VARCHAR(255)
    create_table_query = f"CREATE TABLE {table_name} ({columns});"
    cursor.execute(create_table_query)

def upload_sql_data(table_name, data):
    """
    上传数据到 SQL 数据库
    """
    connection = connect_to_sql()
    cursor = connection.cursor()
    try:
        for _, row in data.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(query, tuple(row))
        connection.commit()
        return {"message": "Data uploaded successfully to SQL!"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        connection.close()

def parse_nlp_query_with_templates(nlp_input):
    """
    解析自然语言输入并生成 SQL 查询
    """
    nlp_input = nlp_input.lower()
    
    if "total sales by product category" in nlp_input:
        return {
            "query": """
                SELECT p.category AS product_category, SUM(t.amount) AS total_sales
                FROM Transactions t
                JOIN Products p ON t.product_id = p.product_id
                GROUP BY p.category;
            """,
            "description": "Total sales grouped by product category"
        }
    elif "total sales by store location" in nlp_input:
        return {
            "query": """
                SELECT t.store_location, SUM(t.amount) AS total_sales
                FROM Transactions t
                GROUP BY t.store_location;
            """,
            "description": "Total sales grouped by store location"
        }
    elif "most active users" in nlp_input:
        return {
            "query": """
                SELECT t.user_id, COUNT(*) AS transaction_count
                FROM Transactions t
                GROUP BY t.user_id
                ORDER BY transaction_count DESC
                LIMIT 10;
            """,
            "description": "Users ranked by transaction count"
        }
    elif "top products by sales" in nlp_input:
        return {
            "query": """
                SELECT p.product_name, SUM(t.amount) AS total_sales
                FROM Transactions t
                JOIN Products p ON t.product_id = p.product_id
                GROUP BY p.product_name
                ORDER BY total_sales DESC
                LIMIT 5;
            """,
            "description": "Top 5 products ranked by total sales"
        }
    elif "average transaction amount by user" in nlp_input:
        return {
            "query": """
                SELECT t.user_id, AVG(t.amount) AS avg_transaction
                FROM Transactions t
                GROUP BY t.user_id
                HAVING avg_transaction > 100;
            """,
            "description": "Average transaction amount by user (above $100)"
        }
    elif "show me the top" in nlp_input and "by" in nlp_input:
        category = extract_category(nlp_input, ["product", "location", "user"])
        metric = extract_metric(nlp_input, ["sales", "transactions"])
        return {
            "query": f"""
                SELECT {category}, SUM({metric}) AS total
                FROM Transactions
                GROUP BY {category}
                ORDER BY total DESC
                LIMIT 10;
            """,
            "description": f"Top 10 {category}s by {metric}"
        }
    else:
        return {"error": "Query could not be matched to a known pattern"}

def test_generate_sample_queries():
    table_name = "test_table"
    result = generate_advanced_sample_queries(table_name)
    assert "sample_queries" in result, "Sample queries not generated"
    assert len(result["sample_queries"]) > 0, "No queries generated"
    print("All tests passed!")

@app.route('/generate_advanced_sample_queries', methods=['GET'])
def generate_advanced_sample_queries_endpoint():
    table_name = request.args.get('table_name')
    if not table_name:
        return jsonify({"error": "Table name is required"}), 400

    result = generate_advanced_sample_queries(table_name)
    return jsonify(result)

def generate_advanced_sample_queries(table_name):
    """
    根据表的结构动态生成多样化的复杂样例查询
    """
    connection = connect_to_sql()
    try:
        with connection.cursor() as cursor:
            # 获取表的列结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            numeric_columns = [col[0] for col in columns if col[1].startswith("int") or col[1].startswith("float")]

            if len(column_names) < 2 or len(numeric_columns) < 1:
                return {"error": "Table must have at least two columns and one numeric column for complex queries"}

            # 随机选择列名和动态值
            col1 = random.choice(column_names)
            col2 = random.choice(column_names)
            numeric_col = random.choice(numeric_columns)
            random_limit = random.randint(5, 20)
            random_value = random.randint(10, 100)

            # 定义复杂查询模板
            queries = [
                f"SELECT {col1}, COUNT(*) FROM {table_name} GROUP BY {col1} ORDER BY COUNT(*) DESC LIMIT {random_limit};",
                f"SELECT {numeric_col}, AVG({numeric_col}) AS avg_value FROM {table_name} GROUP BY {numeric_col} HAVING avg_value > {random_value};",
                f"SELECT a.{col1}, b.{col2} FROM {table_name} a JOIN {table_name} b ON a.{col1} = b.{col1} LIMIT {random_limit};",
                f"SELECT {col1}, SUM({numeric_col}) AS total FROM {table_name} WHERE {numeric_col} > {random_value} GROUP BY {col1} ORDER BY total DESC;",
                f"SELECT {col1} FROM {table_name} WHERE {col2} LIKE '%example%' LIMIT {random_limit};",
                f"SELECT DISTINCT {col1} FROM {table_name} WHERE {numeric_col} BETWEEN {random_value} AND {random_value + 50} LIMIT {random_limit};",
                f"SELECT {col1}, {col2} FROM {table_name} WHERE {numeric_col} < {random_value} ORDER BY {col2} ASC LIMIT {random_limit};"
            ]

            # 返回随机选择的样例查询
            return {"sample_queries": random.sample(queries, min(3, len(queries)))}
    except Exception as e:
        return {"error": f"Failed to generate advanced sample queries: {str(e)}"}
    finally:
        connection.close()



def generate_sample_query_dynamic(table_name):
    """
    动态生成样例查询，涵盖不同语言构造，支持动态列名
    """
    connection = connect_to_sql('project_db')  # 固定数据库名称
    try:
        with connection.cursor() as cursor:
            # 获取列名
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [row[0] for row in cursor.fetchall()]

        # 如果表没有列，则直接返回空
        if not columns:
            return {"error": f"Table {table_name} has no columns"}
        
        col1 = random.choice(columns)  # 随机选择一列
        col2 = random.choice(columns) if len(columns) > 1 else col1  # 随机选择第二列（如果存在）
        
        constructs = [
            # 简单查询
            f"SELECT * FROM {table_name} LIMIT 5;",
            f"SELECT COUNT(*) FROM {table_name};",

            # 动态列名查询
            f"SELECT {col1}, COUNT(*) FROM {table_name} GROUP BY {col1};",
            f"SELECT {col1}, {col2} FROM {table_name} WHERE {col1} IS NOT NULL LIMIT 10;",

            # 聚合查询
            f"SELECT {col1}, SUM({col2}) AS total_sales FROM {table_name} GROUP BY {col1};",

            # 条件过滤
            f"SELECT {col1} FROM {table_name} WHERE {col2} > 100;"
        ]
        return random.sample(constructs, 3)  # 随机返回 3 个样例查询
    except Exception as e:
        return {"error": f"Failed to generate sample queries: {str(e)}"}
    finally:
        connection.close()


@app.route('/')
def home():
    """
    首页：自然语言查询和样例查询
    """
    return render_template('index.html')

@app.route('/execute_query', methods=['POST'])
def execute_query():
    """
    执行自然语言或直接 SQL 查询，并返回 JSON 结果，包括自然语言解析
    """
    user_input = request.json.get('query', '').strip()
    if not user_input:
        return jsonify({"error": "Query cannot be empty"})

    try:
        # 判断是否为直接 SQL 命令
        if user_input.lower().startswith(("select", "insert", "update", "delete")):
            result = execute_sql_query(user_input)  # 执行直接 SQL 查询
            description = generate_query_description(user_input)  # 自动生成描述
            return jsonify({
                "description": description,
                "query": user_input,
                "result": result
            })
        else:
            # 如果是自然语言查询，解析为 SQL
            parsed_query = parse_nlp_query_with_templates(user_input)
            if "error" in parsed_query:
                return jsonify(parsed_query)  # 如果解析失败，返回错误信息
            
            # 执行解析后的 SQL 查询
            result = execute_sql_query(parsed_query["query"])
            description = parsed_query.get("description", generate_query_description(parsed_query["query"]))
            return jsonify({
                "description": description,
                "query": parsed_query["query"],
                "result": result
            })
    except Exception as e:
        return jsonify({"error": f"SQL Error: {str(e)}"})

def generate_query_description(query):
    """
    根据 SQL 查询生成自然语言描述
    """
    query = query.upper()  # 统一转换为大写
    description_parts = []

    # 处理 SELECT 子句
    if "SELECT" in query:
        select_clause = query.split("FROM")[0].replace("SELECT", "").strip()
        description_parts.append(f"The query selects the following columns: {select_clause}.")

    # 处理 FROM 子句
    if "FROM" in query:
        from_clause = query.split("FROM")[1]
        from_table = (
            from_clause.split("WHERE")[0]
            .split("GROUP BY")[0]
            .split("ORDER BY")[0]
            .split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"It retrieves data from the table: {from_table}.")

    # 处理 WHERE 子句
    if "WHERE" in query:
        where_clause = query.split("WHERE")[1]
        where_conditions = (
            where_clause.split("GROUP BY")[0]
            .split("ORDER BY")[0]
            .split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"Filter condition applied: {where_conditions}.")

    # 处理 GROUP BY 子句
    if "GROUP BY" in query:
        group_by_clause = query.split("GROUP BY")[1]
        group_columns = (
            group_by_clause.split("ORDER BY")[0]
            .split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"The data is grouped by the following columns: {group_columns}.")

    # 处理 HAVING 子句
    if "HAVING" in query:
        having_clause = query.split("HAVING")[1]
        having_conditions = (
            having_clause.split("ORDER BY")[0]
            .split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"Filter condition applied to grouped data: {having_conditions}.")

    # 处理 ORDER BY 子句
    if "ORDER BY" in query:
        order_by_clause = query.split("ORDER BY")[1]
        order_columns = (
            order_by_clause.split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"The results are ordered by: {order_columns}.")

    # 处理 LIMIT 子句
    if "LIMIT" in query:
        limit_clause = query.split("LIMIT")[1].strip()
        description_parts.append(f"The results are limited to {limit_clause} rows.")

    # 处理 JOIN 子句
    if "JOIN" in query:
        join_part = query.split("JOIN")[1]
        join_table = join_part.split("ON")[0].strip()
        join_condition = (
            join_part.split("ON")[1].split("WHERE")[0]
            .split("GROUP BY")[0]
            .split("ORDER BY")[0]
            .split("LIMIT")[0]
            .strip()
        )
        description_parts.append(f"The query joins with the table: {join_table}, using the condition: {join_condition}.")

    return " ".join(description_parts)



@app.route('/list_files', methods=['GET'])
def list_files():
    """
    获取当前上传的文件列表
    """
    try:
        files = os.listdir(UPLOAD_FOLDER)  # 获取上传目录中的文件
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"Failed to list files: {str(e)}"}), 500


@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    """
    数据上传页面
    """
    if request.method == 'POST':
        table_name = request.form.get('table_name')
        file = request.files.get('file')

        if not table_name or not file:
            return render_template('upload.html', error="Both table name and file are required")

        try:
            data = pd.read_csv(file)
            upload_result = upload_sql_data(table_name, data)
            return render_template('upload.html', message=upload_result["message"])
        except Exception as e:
            return render_template('upload.html', error=str(e))

    return render_template('upload.html')

@app.route('/sample_query', methods=['GET'])
def sample_query_page():
    """
    样例查询页面
    """
    table_name = request.args.get('table_name', '')
    if not table_name:
        return render_template('sample_query.html', error="Table name is required")

    queries = generate_sample_query_dynamic(table_name)
    return render_template('sample_query.html', queries=queries)

@app.route('/execute_nosql_query', methods=['POST'])
def execute_nosql_query():
    """
    执行 NoSQL 查询
    """
    user_input = request.json.get('query', '')
    if not user_input:
        return jsonify({"error": "Query cannot be empty"})

    try:
        # 示例：根据 NoSQL 数据库处理逻辑
        # result = perform_nosql_query(user_input)
        result = [{"example_field": "example_value"}]  # 示例结果
        return jsonify({
            "description": "NoSQL query executed",
            "query": user_input,
            "result": result
        })
    except Exception as e:
        return jsonify({"error": f"NoSQL Error: {str(e)}"})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    上传 CSV 文件并将内容插入到指定表，同时记录文件名。如果表不存在则创建表，存在则追加数据。
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    table_name = request.form.get('table_name', '').strip()  # 获取目标表名

    if not table_name:
        return jsonify({"error": "Table name is required"}), 400

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # 保存文件到服务器
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # 检查是否是有效 CSV 文件
        try:
            data = pd.read_csv(filepath)
            if data.empty or data.columns.size == 0:
                return jsonify({"error": "Uploaded file is empty or has no columns to parse."}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to parse file: {str(e)}"}), 400

        # 连接数据库
        conn = connect_to_sql('project_db')
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # 如果表不存在，则创建新表
            columns = ", ".join([f"{col} VARCHAR(255)" for col in data.columns])
            create_table_query = f"CREATE TABLE {table_name} ({columns})"
            cursor.execute(create_table_query)

        # 插入数据到表（新建或已存在）
        for _, row in data.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            update_query = ', '.join([f"{col}=VALUES({col})" for col in data.columns])
            query = f"""
            INSERT INTO {table_name} ({', '.join(row.index)}) VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_query};
            """
            cursor.execute(query, tuple(row))

        conn.commit()
        rows_inserted = len(data)

        # 清理
        cursor.close()
        conn.close()
        os.remove(filepath)

        return jsonify({"message": f"File uploaded successfully! Rows inserted: {rows_inserted}"})
    except Exception as e:
        app.logger.error(f"Error uploading file: {str(e)}")
        app.logger.error(f"Error inserting data into table {table_name}: {str(e)}")
        return jsonify({"error": f"Failed to insert data: {str(e)}"}), 500

@app.route('/get_tables', methods=['GET'])
def get_tables():
    """
    获取数据库中的所有表名
    """
    connection = None
    try:
        connection = connect_to_sql('project_db')  # 使用固定数据库
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]  # 提取表名
            return jsonify({"tables": tables})  # 返回表名列表
    except Exception as e:
        return jsonify({"error": f"Failed to fetch tables: {str(e)}"}), 500
    finally:
        if connection:
            connection.close()

@app.route('/generate_sample_queries', methods=['GET'])
def generate_sample_queries():
    table_name = request.args.get('table_name')
    if not table_name:
        return jsonify({"error": "Table name is required"}), 400

    try:
        connection = connect_to_sql('project_db')
        with connection.cursor() as cursor:
            # 获取表结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [row[0] for row in columns]
            numeric_columns = [col[0] for col in columns if col[1].startswith("int") or col[1].startswith("float")]

            if not column_names or not numeric_columns:
                return jsonify({"error": f"Table '{table_name}' must have at least one numeric and one categorical column."})

            # 增加随机性逻辑
            col1 = random.choice(column_names)  # 随机选择分类字段
            col2 = random.choice(numeric_columns)  # 随机选择数值字段

            # 多样化查询模板
            templates = [
                f"SELECT {col1}, SUM({col2}) AS total FROM {table_name} WHERE {col2} > {random.randint(10, 100)} GROUP BY {col1};",
                f"SELECT {col1}, AVG({col2}) AS avg_value FROM {table_name} WHERE {col2} < {random.randint(50, 200)} GROUP BY {col1} ORDER BY avg_value DESC;",
                f"SELECT {col1}, {col2} FROM {table_name} WHERE {col2} BETWEEN {random.randint(1, 50)} AND {random.randint(51, 100)} LIMIT {random.randint(5, 20)};",
                f"SELECT DISTINCT {col1} FROM {table_name} LIMIT {random.randint(5, 15)};",
                f"SELECT COUNT(*) AS total_count FROM {table_name} WHERE {col2} > {random.randint(20, 80)};"
            ]

            # 自然语言描述模板
            descriptions = [
                f"Group the rows of {table_name} by {col1} and calculate the total sum of {col2} for rows where {col2} is greater than a random value.",
                f"Group the rows of {table_name} by {col1}, calculate the average of {col2}, and order the groups in descending order of average values for rows where {col2} is less than a random value.",
                f"Select {col1} and {col2} from {table_name} for rows where {col2} is between two random values, limiting the results to a random number of rows.",
                f"Select distinct values of {col1} from {table_name}, limiting the results to a random number of rows.",
                f"Count the total number of rows in {table_name} where {col2} is greater than a random value."
            ]

            # 生成查询和对应描述，并随机选择
            queries_with_descriptions = [
                f"{query}\n-- {description}"
                for query, description in zip(templates, descriptions)
            ]

            # 随机抽取三条
            selected_queries = random.sample(queries_with_descriptions, min(3, len(queries_with_descriptions)))

            return jsonify({"sample_queries": selected_queries})
    except Exception as e:
        return jsonify({"error": f"Failed to generate sample queries: {str(e)}"}), 500


@app.route('/get_table_info', methods=['GET'])
def get_table_info():
    table_name = request.args.get('table_name')
    if not table_name:
        return jsonify({"error": "Table name is required"}), 400

    try:
        connection = connect_to_sql('project_db')
        with connection.cursor() as cursor:
            # 获取表的列信息
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_details = [{"name": row[0], "type": row[1]} for row in columns]

            # 获取表的示例数据
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = cursor.fetchall()
            sample_columns = [desc[0] for desc in cursor.description]  # 获取列名
            formatted_sample_data = [dict(zip(sample_columns, row)) for row in sample_data]

            return jsonify({
                "columns": column_details,
                "sample_data": formatted_sample_data
            })
    except Exception as e:
        return jsonify({"error": f"Failed to get table info: {str(e)}"}), 500


@app.route('/generate_construct_queries', methods=['GET'])
def generate_construct_queries():
    table_name = request.args.get('table_name')
    construct = request.args.get('construct')  # 获取查询类型

    if not table_name or not construct:
        return jsonify({"error": "Table name and construct type are required"}), 400

    try:
        connection = connect_to_sql('project_db')
        with connection.cursor() as cursor:
            # 获取表结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [row[0] for row in columns]
            numeric_columns = [col[0] for col in columns if col[1].startswith("int") or col[1].startswith("float")]

            if not column_names or not numeric_columns:
                return jsonify({"error": f"Table '{table_name}' must have at least one numeric and one categorical column."})

            # 随机选择列
            col1 = random.choice(column_names)
            col2 = random.choice(numeric_columns)
            random_limit = random.randint(5, 20)
            random_value = random.randint(10, 100)

            # 根据 construct 类型生成查询
            if construct == 'group_by':
                query = f"SELECT {col1}, SUM({col2}) AS total FROM {table_name} GROUP BY {col1};"
            elif construct == 'having':
                query = f"SELECT {col1}, AVG({col2}) AS avg_value FROM {table_name} GROUP BY {col1} HAVING avg_value > {random_value};"
            elif construct == 'join':
                query = f"SELECT a.{col1}, b.{col2} FROM {table_name} a JOIN OtherTable b ON a.id = b.id LIMIT {random_limit};"
            elif construct == 'order_by':
                query = f"SELECT {col1}, {col2} FROM {table_name} ORDER BY {col2} DESC LIMIT {random_limit};"
            elif construct == 'where':
                query = f"SELECT {col1}, {col2} FROM {table_name} WHERE {col2} > {random_value} LIMIT {random_limit};"
            else:
                return jsonify({"error": "Invalid construct type"}), 400

            # 生成自然语言描述
            description = generate_query_description(query)

            return jsonify({"query": query, "description": description})
    except Exception as e:
        return jsonify({"error": f"Failed to generate construct query: {str(e)}"}), 500



def connect_to_mongo():
    client = MongoClient(
        host='13.57.241.139',  # Replace with your EC2 public IP address
        port=27017  # MongoDB default port
    )
    db = client['orders']  # Replace with your MongoDB database name
    return db

@app.route('/mongo/explore', methods=['GET'])
def explore_database():
    db = connect_to_mongo()
    collections = db.list_collection_names()
    collections_info = {}

    for collection_name in collections:
        collection = db[collection_name]
        sample_data = collection.find_one()  # Get one document as a sample
        if sample_data:
            fields = sample_data.keys()
            collections_info[collection_name] = {
                "fields": list(fields),
                "sample_data": json_util.loads(json_util.dumps(sample_data))
            }
        else:
            collections_info[collection_name] = {
                "fields": [],
                "sample_data": "No data available"
            }

    return Response(json_util.dumps(collections_info), mimetype='application/json')

@app.route('/mongo/sample_queries', methods=['GET'])
def get_sample_queries():
    db = connect_to_mongo()
    collections = db.list_collection_names()

    if not collections:
        return jsonify({"error": "No collections available in the database."}), 400

    query_patterns = [
        {
            "description": "Find documents with a condition on a specific field.",
            "query": lambda collection, field: f"db.{collection}.find({{{field}: {{'$gt': <value>}}}})"
        },
        {
            "description": "Aggregation example: group by a field and count documents.",
            "query": lambda collection, field: f"db.{collection}.aggregate([{{'$group': {{'_id': '${field}', 'count': {{'$sum': 1}}}}}}])"
        },
        {
            "description": "Find documents sorted by a field in descending order.",
            "query": lambda collection, field: f"db.{collection}.find().sort({{{field}: -1}})"  # Sort descending
        }
    ]

    selected_queries = random.sample(query_patterns, min(3, len(query_patterns)))
    sample_queries = []

    for query_info in selected_queries:
        collection = random.choice(collections)
        sample_data = db[collection].find_one()

        if sample_data:
            fields = list(sample_data.keys())
            field = random.choice(fields)
            sample_queries.append({
                "description": query_info["description"],
                "query": query_info["query"](collection, field)
            })

    return jsonify(sample_queries)

@app.route('/mongo/natural_language_query', methods=['POST'])
def execute_mongo_query():
    try:
        # 获取 JSON 请求体
        data = request.get_json()
        print("Received Data:", data)  # 调试信息

        # 验证参数是否存在
        query = data.get('query')
        collection_name = data.get('collection')

        if not query or not collection_name:
            return jsonify({"error": "Both 'query' and 'collection' are required"}), 400

        # 转换查询字符串为字典（如果需要）
        if isinstance(query, str):
            query = eval(query)  # 将字符串形式的查询转换为字典，需确保安全性

        # 连接 MongoDB 并执行查询
        db = connect_to_mongo()
        collection = db[collection_name]

        result = list(collection.find(query).sort("_id", -1))  # 按字段排序
        return jsonify({"result": result})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500




def generate_query(query):
    action, collection = parse_query(query)
    
    if not action or not collection:
        return {"error": "Could not determine action or target collection from the input."}

    # 根据 action 和 collection 生成查询
    if action == 'find':
        mongo_query = f"db.{collection}.find({{}}).limit(10)"
    elif action == 'count':
        mongo_query = f"db.{collection}.countDocuments({{}})"
    elif action == 'sort':
        mongo_query = f"db.{collection}.find({{}}).sort({{ 'totalAmount': 1 }}).limit(10)"
    elif action == 'group':
        mongo_query = f"db.{collection}.aggregate([{{ '$group': {{ '_id': '$category', 'total': {{ '$sum': 1 }} }} }}])"
    else:
        mongo_query = {"error": "Unknown action."}

    return mongo_query

def parse_query(query):
    query = query.lower()

    collections = ['products', 'orders', 'reviews', 'categories', 'users']
    actions = {
        'find': ['find', 'list', 'show'],
        'count': ['count', 'how many'],
        'sort': ['sort', 'order by'],
        'group': ['group by', 'aggregate'],
    }

    collection = None
    for col in collections:
        if col in query:
            collection = col
            break

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)