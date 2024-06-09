from flask import Flask, render_template, request, jsonify
import mysql.connector



app = Flask(__name__)

# Establish connection to MySQL server
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345678',
    database='restaurant_db'
)
cursor = conn.cursor()

# Create MenuItems table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS MenuItems (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        item_name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        category VARCHAR(50)
    )
''')

# Create Orders table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_name VARCHAR(255) NOT NULL,
        table_number INT NOT NULL,
        date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2) NOT NULL
    )
''')

# Create OrderItems table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        order_item_id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT,
        item_id INT,
        quantity INT,
        subtotal DECIMAL(10, 2),
        FOREIGN KEY (order_id) REFERENCES Orders(order_id),
        FOREIGN KEY (item_id) REFERENCES MenuItems(item_id)
    )
''')

# Commit changes
conn.commit()

print("Database and tables created successfully.")

# Frontend: Home page to display menu
@app.route('/')
def index():
    # Establish connection to MySQL server
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='restaurant_db'
    )
    cursor = conn.cursor()
    
    # Fetch menu items from the database
    cursor.execute('SELECT * FROM MenuItems')
    menu_items = cursor.fetchall()
    
    # Convert fetched data to list of dictionaries
    menu_items_dict = []
    for item in menu_items:
        item_dict = {
            'item_id': item[0],
            'item_name': item[1],
            'description': item[2],
            'price': float(item[3]),  # Convert price to float
            'category': item[4]
        }
        menu_items_dict.append(item_dict)

    # Close connection
    conn.close()

    # Pass menu_items_dict to the HTML template
    return render_template('index.html', menu_items=menu_items_dict)

# API endpoint to place an order
@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    customer_name = data['customer_name']
    table_number = data['table_number']
    order_items = data['order_items']
    
    # Establish connection to MySQL server
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='restaurant_db'
    )
    cursor = conn.cursor()
    
    # Calculate total amount
    total_amount = sum(item['price'] * item['quantity'] for item in order_items)
    
    # Insert order into Orders table
    cursor.execute('INSERT INTO Orders (customer_name, table_number, total_amount) VALUES (%s, %s, %s)',
                   (customer_name, table_number, total_amount))
    order_id = cursor.lastrowid
    
    # Insert order items into OrderItems table
    for item in order_items:
        item_id = item['item_id']
        quantity = item['quantity']
        subtotal = item['price'] * quantity
        cursor.execute('INSERT INTO OrderItems (order_id, item_id, quantity, subtotal) VALUES (%s, %s, %s, %s)',
               (order_id, item_id, quantity, subtotal))

    # Commit changes
    conn.commit()
    
    # Close connection
    conn.close()
    
    return jsonify({'message': 'Order placed successfully'})

# Route for order success page
@app.route('/order_success')
def order_success():
    # Fetch the latest order details
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',
        database='restaurant_db'
    )
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Orders ORDER BY order_id DESC LIMIT 1')
    latest_order = cursor.fetchone()

    cursor.execute('SELECT * FROM OrderItems WHERE order_id = %s', (latest_order[0],))
    order_items = cursor.fetchall()

    # Close connection
    conn.close()

    return render_template('order_success.html', latest_order=latest_order, order_items=order_items)


if __name__ == '__main__':
    app.run(debug=True)
