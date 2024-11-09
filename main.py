import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid
import os

# Initialize Flask app
app = Flask(__name__, template_folder='templates')  # Specify template folder if necessary

app.secret_key = 'your_secret_key'

# Initialize SQLite database
DATABASE = 'pharmacy_inventory.db'

# Function to get a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create a table for the pharmacy inventory if it doesn't exist
def init_db():
    conn = get_db()
    with conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            expiration_date TEXT NOT NULL
        )
        ''')
    conn.close()

# Home page: Display all medicines in the inventory
@app.route('/')
def index():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        inventory = cursor.fetchall()
        return render_template('index.html', inventory=inventory)
    except Exception as e:
        flash(f"Error fetching data: {e}", "danger")
        return render_template('index.html', inventory=[])

# Add a new medicine to the inventory
@app.route('/add', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        expiration_date = request.form['expiration_date']

        # Validate expiration date format
        try:
            datetime.strptime(expiration_date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid expiration date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('add_medicine'))

        # Generate a unique ID for the medicine
        medicine_id = str(uuid.uuid4())

        # Add the medicine to the database
        try:
            conn = get_db()
            with conn:
                conn.execute('''
                INSERT INTO inventory (id, name, quantity, price, expiration_date)
                VALUES (?, ?, ?, ?, ?)
                ''', (medicine_id, name, quantity, price, expiration_date))
            flash(f"Medicine '{name}' added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error adding medicine: {e}", "danger")
            return redirect(url_for('add_medicine'))

    return render_template('add_medicine.html')

# Edit an existing medicine
@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        expiration_date = request.form['expiration_date']

        # Validate expiration date format
        try:
            datetime.strptime(expiration_date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid expiration date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('edit_medicine', id=id))

        # Update the medicine in the database
        try:
            with conn:
                cursor.execute('''
                UPDATE inventory
                SET name = ?, quantity = ?, price = ?, expiration_date = ?
                WHERE id = ?
                ''', (name, quantity, price, expiration_date, id))
            flash(f"Medicine '{name}' updated successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error updating medicine: {e}", "danger")
            return redirect(url_for('edit_medicine', id=id))

    # Fetch the existing data to pre-fill the form
    cursor.execute("SELECT * FROM inventory WHERE id = ?", (id,))
    medicine = cursor.fetchone()
    conn.close()
    return render_template('edit_medicine.html', medicine=medicine)

# Delete a medicine from the inventory
@app.route('/delete/<string:id>', methods=['GET'])
def delete_medicine(id):
    try:
        conn = get_db()
        with conn:
            conn.execute("DELETE FROM inventory WHERE id = ?", (id,))
        flash("Medicine deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting medicine: {e}", "danger")
    return redirect(url_for('index'))

# Search medicines by name
@app.route('/search', methods=['GET', 'POST'])
def search_medicine():
    if request.method == 'POST':
        search_name = request.form['search_name']
        if search_name:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", ('%' + search_name + '%',))
            inventory = cursor.fetchall()
            return render_template('index.html', inventory=inventory)
        else:
            flash("Please enter a medicine name to search.", "danger")
            return redirect(url_for('index'))
    return redirect(url_for('index'))

# Run the Flask app
if __name__ == "__main__":
    init_db()  # Create the table if it doesn't exist
    print("Templates Folder Path:", os.path.abspath('templates'))
    app.run(host="0.0.0.0", port=5000, debug=True)
