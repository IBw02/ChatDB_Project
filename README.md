
# ChatDB Project

## Overview

The ChatDB Project is a web-based application that allows users to interact with a database using both SQL queries (Custom Query) and Natural Language Queries (NLP Query). This project bridges the gap between technical SQL knowledge and user-friendly natural language processing, providing an intuitive way to explore and analyze data.

---

## Features

- **Custom Query**: Execute direct SQL queries on the database.
- **Natural Language Query**: Use natural language to generate SQL queries dynamically.
- **Database Integration**: Supports both local and remote MySQL databases.
- **Interactive UI**: User-friendly interface to input queries and view results.
- **Error Handling**: Comprehensive error handling with descriptive feedback.
- **Example Queries**: Includes predefined examples for both query types.

---

## Requirements

- Python 3.8 or higher
- Flask
- pymysql
- A MySQL database (local or hosted on EC2)
- Frontend: HTML, CSS (Bootstrap), JavaScript

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository_url>
cd ChatDB_Project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the database
Update the database connection details in `app.py`:
```python
def connect_to_remote_db():
    return pymysql.connect(
        host="your-database-host",
        user="your-database-user",
        password="your-database-password",
        database="your-database-name",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
```

### 4. Start the Flask application
```bash
python app.py
```

### 5. Access the application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Usage

### **Custom Query**
1. Go to the **Custom Query** section.
2. Enter a valid SQL query (e.g., `SELECT * FROM amazon_products LIMIT 10;`).
3. Click **Run Query**.
4. View the results on the same page.

### **Natural Language Query**
1. Go to the **Natural Language Query** section.
2. Enter a query in natural language (e.g., `Find products with price below 300 and rating above 4.`).
3. Click **Run Query**.
4. View the dynamically generated SQL and the results on the next page.

---

## Example Queries

### **Custom Query Examples**
- `SELECT * FROM amazon_products LIMIT 10;`
- `SELECT category, AVG(rating) AS avg_rating FROM amazon_products GROUP BY category ORDER BY avg_rating DESC LIMIT 5;`
- `SELECT product_name, discounted_price FROM amazon_products WHERE discounted_price < 300 ORDER BY discounted_price ASC;`

### **Natural Language Query Examples**
- `Show top 10 products.`
- `Find products with price below 300 and rating above 4.`
- `What is the average rating for each category?`
- `Show the most discounted products in Computers.`

---

## Troubleshooting

### Common Issues
- **Database connection error**: Ensure the database credentials in `app.py` are correct.
- **Natural Language Query not recognized**: Ensure the input follows supported query patterns (see Example Queries).
- **Missing dependencies**: Run `pip install -r requirements.txt` to install all required libraries.

---

## Project Structure

```
ChatDB_Project/
├── app.py             # Main application script
├── templates/         # HTML templates (index, results, error pages)
│   ├── index.html
│   ├── results.html
│   └── error.html
├── static/            # Static files (CSS, JS, etc.)
├── requirements.txt   # List of dependencies
├── README.md          # Project documentation
```

---

## Contributions

If you have suggestions or improvements, feel free to create a pull request or raise an issue.

---

## Contact

For any issues or questions, please contact the project team:
- **Wayne Wang**: waynewang229@gmail.com
