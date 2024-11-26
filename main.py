from mongodb import connect_to_mongo, explore_database, show_sample_queries, generate_queries, nlp_examples, upload_json_to_mongodb, test_query
from sql import connect_to_sql, show_database_structure, show_sample_sql_queries, generate_sql_queries, nlp_to_sql, upload_data_to_sql, execute_user_query

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
                print("5. Upload Data")
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
                print("5. Upload Data")
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