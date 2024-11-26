from pymongo import MongoClient
import random
import json
import re

def connect_to_mongo():
    client = MongoClient(
        host='13.57.241.139',  # Replace with your EC2 public IP address
        port=27017  # MongoDB default port
    )
    db = client['orders']  # Replace with your MongoDB database name
    return db

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