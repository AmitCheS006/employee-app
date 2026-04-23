import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "employees.db"
EXCEL_FILE = "project work sheet.xlsx"

def init_db():
    """Initializes the database only if it doesn't exist."""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        try:
            print("Database not found. Importing from Excel...")
            df = pd.read_excel(EXCEL_FILE)
            # Clean column names (lowercase, no spaces) and fill empty cells
            df.columns = [col.lower().strip() for col in df.columns]
            df = df.fillna('')
            
            # Create table from Excel data
            df.to_sql("employees", conn, if_exists="replace", index=False)
            print(f"Successfully imported {len(df)} records.")
        except Exception as e:
            print(f"Error during initialization: {e}")
        finally:
            conn.close()
    else:
        print("Database already exists. Skipping Excel import.")

@app.route('/')
@app.route('/')
@app.route('/')
def index():
    query = request.args.get('q', '').strip() # Gets the text from the search box
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if query:
        # This searches NAME, SAIL_PERNO, or PAN columns
        search_param = f'%{query}%'
        cursor.execute("""
            SELECT * FROM employees 
            WHERE name LIKE ? OR sail_perno LIKE ? OR pan LIKE ?
        """, (search_param, search_param, search_param))
    else:
        cursor.execute("SELECT * FROM employees")

    data = cursor.fetchall()
    conn.close()
    return render_template("index.html", data=data, query=query)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Mapping form fields to specific DB columns
        employee_data = (
            request.form.get('sail_perno'),
            request.form.get('name'),
            request.form.get('grade'),
            request.form.get('designation'),
            request.form.get('accno'),
            request.form.get('pan'),
            request.form.get('doj'),
            request.form.get('dob'),
            request.form.get('uanno')
        )

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO employees (sail_perno, name, grade, designation, accno, pan, doj, dob, uanno)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, employee_data)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
        
        return redirect(url_for('index'))

    return render_template("add.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)