import pymysql

# Connect to the remote MySQL database
def connect_to_remote_db():
    return pymysql.connect(
        host='ec2-54-193-110-162.us-west-1.compute.amazonaws.com',  # Replace with your EC2 public IP
        user='root',  # MySQL username
        password='Dsci-551',  # MySQL password
        database='amazon_data'  # Database name
    )

# Execute a query and display results
def query_database(sql_query):
    try:
        connection = connect_to_remote_db()
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            for row in result:
                print(row)  # Print the results
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

# Predefined query menu
def predefined_query_menu():
    predefined_queries = {
        "1": {
            "description": "View top-rated product categories",
            "query": """
                SELECT category, AVG(rating) AS avg_rating
                FROM amazon_products
                GROUP BY category
                ORDER BY avg_rating DESC
                LIMIT 5;
            """
        },
        "2": {
            "description": "View best-selling products",
            "query": """
                SELECT product_name, rating_count
                FROM amazon_products
                ORDER BY rating_count DESC
                LIMIT 5;
            """
        },
        "3": {
            "description": "View products with the highest discount",
            "query": """
                SELECT product_name, (actual_price - discounted_price) AS discount_amount
                FROM amazon_products
                ORDER BY discount_amount DESC
                LIMIT 5;
            """
        }
    }

    print("\nPredefined query options:")
    for key, value in predefined_queries.items():
        print(f"{key}: {value['description']}")

    choice = input("\nEnter the number of your choice (or press Enter to exit): ")
    if choice in predefined_queries:
        print(f"\nExecuting query: {predefined_queries[choice]['description']}")
        query_database(predefined_queries[choice]['query'])
    else:
        print("Invalid choice or exiting!")

if __name__ == "__main__":
    while True:
        print("\nWelcome to the Remote Database Query System!")
        print("1: Enter a custom SQL query")
        print("2: Choose from predefined queries")
        print("3: Exit")
        
        option = input("\nSelect an option: ")
        if option == "1":
            user_query = input("\nEnter your SQL query: ")
            query_database(user_query)
        elif option == "2":
            predefined_query_menu()
        elif option == "3":
            print("\nExiting the program. Goodbye!")
            break
        else:
            print("Invalid option. Please try again!")
