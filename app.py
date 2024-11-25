from flask import Flask, request, render_template
import pymysql
import re

app = Flask(__name__)

# Database connection function
def connect_to_remote_db():
    return pymysql.connect(
        host='ec2-54-193-110-162.us-west-1.compute.amazonaws.com',  # Replace with your EC2 public IP
        user='root',  # MySQL username
        password='Dsci-551',  # MySQL password
        database='amazon_data'  # Database name
    )

def extract_keywords(nlp_input):
    # 转换为小写
    nlp_input = nlp_input.lower()

    # 提取数字
    numbers = [int(num) for num in re.findall(r'\b\d+\b', nlp_input)]

    # 提取条件关键词
    conditions = re.findall(r'(price below|rating above|discount over)', nlp_input)

    return {
        "numbers": numbers,
        "conditions": conditions,
        "keywords": nlp_input.split()
    }

def parse_conditions(conditions):
    sql_conditions = []
    for cond in conditions:
        if "price below" in cond:
            value = int(re.search(r'\d+', cond).group())
            sql_conditions.append(f"discounted_price < {value}")
        elif "rating above" in cond:
            value = float(re.search(r'\d+(\.\d+)?', cond).group())
            sql_conditions.append(f"rating > {value}")
        elif "discount over" in cond:
            value = int(re.search(r'\d+', cond).group())
            sql_conditions.append(f"(actual_price - discounted_price) > {value}")
    return " AND ".join(sql_conditions)


@app.route('/')
def home():
    return render_template('index.html')

# Predefined queries dictionary
PREDEFINED_QUERIES = {
    "top_categories": """
        SELECT category, AVG(rating) AS avg_rating
        FROM amazon_products
        GROUP BY category
        ORDER BY avg_rating DESC
        LIMIT 5;
    """,
    "best_selling": """
        SELECT product_name, rating_count
        FROM amazon_products
        ORDER BY rating_count DESC
        LIMIT 5;
    """,
    "highest_discount": """
        SELECT product_name, (COALESCE(actual_price, 0) - COALESCE(discounted_price, 0)) AS discount_amount
        FROM amazon_products
        ORDER BY discount_amount DESC
        LIMIT 5;
    """
}

@app.route('/predefined_query', methods=['GET'])
def predefined_query():
    query_type = request.args.get('type')
    if query_type in PREDEFINED_QUERIES:
        try:
            connection = connect_to_remote_db()
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(PREDEFINED_QUERIES[query_type])
                results = cursor.fetchall()
                if not results:  # Check if results are empty
                    return render_template('error.html', error="No results found for this query.")
            return render_template('results.html', results=results, query_type=query_type, page=None, query=None)
        except Exception as e:
            return render_template('error.html', error=str(e))
    else:
        return render_template('error.html', error="Invalid query type")

@app.route('/custom_query', methods=['POST'])
def custom_query():
    sql_query = request.form.get('query')
    page = int(request.form.get('page', 1))  # Default to page 1 if not provided
    limit = int(request.form.get('limit', 10))  # Default to 10 records per page
    offset = (page - 1) * limit

    # Check for dangerous keywords
    forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
    if any(keyword in sql_query.upper() for keyword in forbidden_keywords):
        return render_template('error.html', error="Your query contains forbidden operations.")

    # Remove semicolon if present in the user's query
    sanitized_sql_query = sql_query.rstrip(";")

    # Query to count total records
    count_query = f"SELECT COUNT(*) as total FROM ({sanitized_sql_query}) AS temp_table"

    # Check if LIMIT already exists
    if not re.search(r'\bLIMIT\b', sql_query, re.IGNORECASE):
        paginated_query = f"{sanitized_sql_query} LIMIT {limit} OFFSET {offset}"
    else:
        paginated_query = sql_query

    try:
        connection = connect_to_remote_db()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Execute total count query
            cursor.execute(count_query)
            total_records = cursor.fetchone()["total"]

            # Execute paginated query
            cursor.execute(paginated_query)
            results = cursor.fetchall()

        total_pages = (total_records + limit - 1) // limit  # Calculate total pages
        return render_template(
            'results.html', 
            results=results, 
            query_type="Custom Query", 
            page=page, 
            query=sanitized_sql_query, 
            limit=limit, 
            total_records=total_records, 
            total_pages=total_pages
        )
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/nlp_query', methods=['POST'])
def nlp_query():
    nlp_input = request.form.get('nlp_query')  # 获取用户的自然语言查询

    # Tokenize the input query and convert to lowercase
    tokens = nlp_input.lower().split()
    sql_query = None

    try:
        # Parse the natural language query
        if "highest" in tokens and "categories" in tokens:
            # Query for highest rated categories
            limit = next((int(word) for word in tokens if word.isdigit()), 5)
            sql_query = f"""
                SELECT category, AVG(rating) AS avg_rating
                FROM amazon_products
                GROUP BY category
                ORDER BY avg_rating DESC
                LIMIT {limit};
            """

        elif "best" in tokens and "products" in tokens:
            # Query for most popular products
            limit = next((int(word) for word in tokens if word.isdigit()), 5)
            sql_query = f"""
                SELECT product_name, rating_count
                FROM amazon_products
                ORDER BY rating_count DESC
                LIMIT {limit};
            """

        elif "price below" in nlp_input and "rating above" in nlp_input:
            # Query for products with price below X and rating above Y
            price_limit = next((int(word) for word in tokens if "price" in nlp_input and word.isdigit()), 300)
            rating_threshold = next((float(word) for word in tokens if "rating" in nlp_input and word.replace('.', '', 1).isdigit()), 4.0)
            sql_query = f"""
                SELECT product_name, discounted_price, rating
                FROM amazon_products
                WHERE discounted_price < {price_limit} AND rating > {rating_threshold}
                ORDER BY discounted_price ASC;
            """

        elif "price below" in nlp_input:
            # Query for products below a specific price
            price_limit = next((int(word) for word in tokens if word.isdigit()), 100)
            sql_query = f"""
                SELECT product_name, discounted_price
                FROM amazon_products
                WHERE discounted_price < {price_limit}
                ORDER BY discounted_price ASC;
            """

        elif "most popular products" in nlp_input:
            # Query for most popular products
            sql_query = """
                SELECT product_name, rating_count
                FROM amazon_products
                ORDER BY rating_count DESC
                LIMIT 10;
            """

        elif "average rating" in tokens and "categories" in tokens:
            # Query for average rating of each category
            sql_query = """
                SELECT category, AVG(rating) AS avg_rating
                FROM amazon_products
                GROUP BY category
                ORDER BY avg_rating DESC;
            """

        elif "products with rating above" in nlp_input:
            # Query for products with a rating above a specific value
            rating_threshold = next((float(word) for word in tokens if word.replace('.', '', 1).isdigit()), 4.0)
            sql_query = f"""
                SELECT product_name, rating
                FROM amazon_products
                WHERE rating > {rating_threshold}
                ORDER BY rating DESC;
            """

        elif "top categories by discount" in nlp_input:
            # Query for categories with the highest total discounts
            sql_query = """
                SELECT category, SUM(actual_price - discounted_price) AS total_discount
                FROM amazon_products
                GROUP BY category
                ORDER BY total_discount DESC
                LIMIT 5;
            """

        else:
            return render_template('error.html', error="Unable to process your natural language query. Please try again with a supported query.")

        # Execute the query and fetch results
        connection = connect_to_remote_db()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()

        # Render the results on the results page
        return render_template('results.html', results=results, query_type="NLP Query", query=nlp_input)

    except Exception as e:
        # Capture errors and render the error page
        return render_template('error.html', error=f"Error processing query: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True)
