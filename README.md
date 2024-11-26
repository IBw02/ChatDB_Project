
# **ChatDB Project**

ChatDB is an interactive database management tool that supports both **SQL databases** and **MongoDB databases**. It provides a user-friendly command-line interface for exploring, querying, and uploading data.

---

## **Features**
### **SQL Features:**
- View database structure and sample table data.
- Auto-generate SQL queries.
- Parse natural language to generate SQL queries.
- Upload table data from CSV files.

### **MongoDB Features:**
- List collections and their field information.
- Auto-generate MongoDB queries.
- Parse natural language to generate MongoDB queries.
- Upload collection data from JSON files.

---

## **File Structure**
```plaintext
ChatDB_Project/
│
├── main.py                # Main program providing entry point and menu logic
├── mongodb.py             # MongoDB-related functionality implementation
├── sql.py                 # SQL-related functionality implementation
├── requirements.txt       # List of required dependencies
└── README.md              # Project documentation
```

---

## **Installation**
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/ChatDB_Project.git
cd ChatDB_Project
```

### 2. Create a Virtual Environment and Install Dependencies (Optional)
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Configure the Databases
- **SQL Database**: Update connection details in `sql.py` (e.g., host, username, password, database name).
- **MongoDB Database**: Update connection details in `mongodb.py` (e.g., host and port).

---

## **Running the Project**
To start the program, run:
```bash
python main.py
```

---

## **Usage**
1. After starting the program, you will see a welcome screen. Choose the type of database:
   - Enter `1` for SQL database operations.
   - Enter `2` for MongoDB database operations.
   - Enter `3` to exit the program.

2. Follow the sub-menu prompts to explore tables/collections, generate queries, or upload data.

---

## **Dependencies**
This project relies on:
- `pymysql`: For connecting to SQL databases.
- `pymongo`: For connecting to MongoDB databases.
- `pandas`: For handling CSV data.

Refer to `requirements.txt` for the complete list.

---

## **Developer Information**
- **Authors**: Tengjiang Wang, Zifeng Zhou
- **Academic Context**: This project is part of USC's DSCI 551 course.

For inquiries, contact [Waynewang229@gmail.com](mailto:Waynewang229@gmail.com).
