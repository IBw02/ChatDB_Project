
# ChatDB: Interactive Database Querying Application

ChatDB is a Flask-based web application that enables users to interact with databases using natural language or structured queries. The application supports both SQL and NoSQL databases, with features for exploring databases, generating sample queries, uploading data, and executing queries dynamically.

---

## Features
- **Explore Databases**: View available tables and their attributes in a selected database.
- **Generate Sample Queries**: Dynamically create example queries, including aggregation, filtering, sorting, and joins.
- **Support for Specific SQL Constructs**: Generate queries with specific constructs like `GROUP BY`, `HAVING`, `WHERE`, `JOIN`, and `ORDER BY`.
- **Dynamic Query Type Selection**: Allows users to select the desired SQL construct type from a dropdown menu.
- **Natural Language Queries**: Parse user input to generate and execute SQL queries.
- **File Upload**: Upload CSV files to create or update tables in the database.
- **SQL/NoSQL Toggle**: Support switching between SQL and NoSQL databases (MongoDB support planned).
- **Interactive Web Interface**: User-friendly interface built with HTML, CSS, and JavaScript.

---

## Project Structure
```
├── app.py                # Main Flask application
├── data/                 # Directory for storing database-related files (if any)
├── static/
│   ├── script.js         # Frontend logic for handling user interactions
│   ├── style.css         # CSS file for styling the application
├── templates/
│   ├── index.html        # Main HTML file for rendering the web interface
├── uploads/              # Directory for storing uploaded files
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation (this file)
└── __pycache__/          # Python cache directory
```

---

## Installation

### Prerequisites
- Python 3.10 or later
- MySQL server
- (Optional) MongoDB for NoSQL support

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   - Update the database connection details in `app.py` (e.g., `host`, `user`, `password`, and `database`).
   - Ensure the database schema matches the tables described in `DESCRIBE` commands.

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application:
   Open `http://127.0.0.1:5000` in your web browser.

---

## Usage

### 1. Explore Databases
- View a list of available tables in the database.
- Select a table to view its structure and generate queries.

### 2. Generate Sample Queries
- Choose a table and generate dynamic SQL queries, including `GROUP BY`, `HAVING`, `WHERE`, `JOIN`, and `ORDER BY`.

### 3. Execute Natural Language Queries
- Enter queries like "Show total sales by product category" to automatically generate and execute SQL.

### 4. Upload Data
- Upload CSV files to create or update tables.

### 5. Toggle SQL/NoSQL
- Switch between SQL and NoSQL modes using the provided toggle button.

---

## Development

### File Descriptions
- **`app.py`**: Backend logic for handling routes, database interactions, and query execution.
- **`static/script.js`**: Frontend script for handling UI events and AJAX calls.
- **`static/style.css`**: CSS for styling the application.
- **`templates/index.html`**: HTML template for the web interface.
- **`uploads/`**: Directory for storing uploaded files.

### Endpoints
- `/`: Home page for interacting with the database.
- `/get_tables`: Fetch available tables.
- `/generate_sample_queries`: Generate SQL queries dynamically.
- `/generate_construct_queries`: Generate queries with specific SQL constructs.
- `/upload_file`: Upload CSV files to the database.
- `/execute_query`: Execute SQL queries or natural language queries.

---

## Future Improvements
- Add NoSQL (MongoDB) support.
- Enhance natural language processing for more complex queries.
- Improve UI with advanced interactivity and feedback.

---

## License
This project is open-source and available under the MIT License.

---

## Authors
- **Your Name** (Primary Developer)

---

## Acknowledgments
- Instructor and course materials from DSCI 551.
- Libraries: Flask, PyMySQL, Pandas, and others listed in `requirements.txt`.
