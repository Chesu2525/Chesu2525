import sqlite3
from datetime import datetime

# --- Database Setup ---
conn = sqlite3.connect('chesu_shop.db')
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    sale_date TEXT,
    total_    from flask import Flask, render_template, request, redirect, url_for
    import sqlite3
    from datetime import datetime
    
    app = Flask(__name__)
    
    def get_db_connection():
        conn = sqlite3.connect('chesu_shop.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/products')
    def products():
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return render_template('products.html', products=products)
    
    @app.route('/add_product', methods=('GET', 'POST'))
    def add_product():
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            conn = get_db_connection()
            conn.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', (name, price, stock))
            conn.commit()
            conn.close()
            return redirect(url_for('products'))
        return render_template('add_product.html')
    
    @app.route('/customers')
    def customers():
        conn = get_db_connection()
        customers = conn.execute('SELECT * FROM customers').fetchall()
        conn.close()
        return render_template('customers.html', customers=customers)
    
    @app.route('/add_customer', methods=('GET', 'POST'))
    def add_customer():
        if request.method == 'POST':
            name = request.form['name']
            phone = request.form['phone']
            conn = get_db_connection()
            conn.execute('INSERT INTO customers (name, phone) VALUES (?, ?)', (name, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('customers'))
        return render_template('add_customer.html')
    
    @app.route('/bills')
    def bills():
        conn = get_db_connection()
        bills = conn.execute('SELECT * FROM sales').fetchall()
        conn.close()
        return render_template('bills.html', bills=bills)
    
    @app.route('/create_bill', methods=('GET', 'POST'))
    def create_bill():
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        customers = conn.execute('SELECT * FROM customers').fetchall()
        if request.method == 'POST':
            customer_id = request.form.get('customer_id')
            if customer_id == '0':
                customer_id = None
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute('INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)', (customer_id, sale_date, 0))
            sale_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            total = 0
            for product in products:
                qty = int(request.form.get(f'qty_{product["product_id"]}', 0))
                if qty > 0:
                    unit_price = product['price']
                    total_price = unit_price * qty
                    conn.execute('INSERT INTO bill_items (sale_id, product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)',
                                 (sale_id, product['product_id'], qty, unit_price, total_price))
                    conn.execute('UPDATE products SET stock = stock - ? WHERE product_id = ?', (qty, product['product_id']))
                    total += total_price
            conn.execute('UPDATE sales SET total_amount=? WHERE sale_id=?', (total, sale_id))
            conn.commit()
            conn.close()
            return redirect(url_for('bills'))
        conn.close()
        return render_template('create_bill.html', products=products, customers=customers)
    
    @app.route('/bill/<int:sale_id>')
    def bill_detail(sale_id):
        conn = get_db_connection()
        bill = conn.execute('SELECT * FROM sales WHERE sale_id=?', (sale_id,)).fetchone()
        items = conn.execute('''
            SELECT products.name, bill_items.quantity, bill_items.unit_price, bill_items.total_price
            FROM bill_items JOIN products ON bill_items.product_id = products.product_id
            WHERE bill_items.sale_id=?
        ''', (sale_id,)).fetchall()
        conn.close()
        return render_template('bill_detail.html', bill=bill, items=items)
    
    if __name__ == '__main__':
        app.run(debug=True)amount REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS bill_items (
    bill_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

conn.commit()

# --- Functions ---
def add_product():
    name = input("Product name: ")
    price = float(input("Price: "))
    stock = int(input("Stock: "))
    c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    print("Product added.")

def add_customer():
    name = input("Customer name: ")
    phone = input("Phone: ")
    c.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    print("Customer added.")

def list_products():
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    print("\nProducts:")
    for p in products:
        print(f"{p[0]}: {p[1]} - GHS {p[2]} (Stock: {p[3]})")
    print()

def create_bill():
    list_products()
    customer_id = int(input("Enter customer ID (or 0 for walk-in): "))
    if customer_id == 0:
        customer_id = None
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sales (customer_id, sale_date, total_amount) VALUES (?, ?, ?)", (customer_id, sale_date, 0))
    sale_id = c.lastrowid
    total = 0
    while True:
        prod_id = int(input("Product ID (0 to finish): "))
        if prod_id == 0:
            break
        c.execute("SELECT name, price, stock FROM products WHERE product_id=?", (prod_id,))
        prod = c.fetchone()
        if not prod:
            print("Invalid product.")
            continue
        qty = int(input(f"Quantity for {prod[0]}: "))
        if qty > prod[2]:
            print("Not enough stock.")
            continue
        unit_price = prod[1]
        total_price = unit_price * qty
        c.execute("INSERT INTO bill_items (sale_id, product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
                  (sale_id, prod_id, qty, unit_price, total_price))
        c.execute("UPDATE products SET stock = stock - ? WHERE product_id = ?", (qty, prod_id))
        total += total_price
    c.execute("UPDATE sales SET total_amount=? WHERE sale_id=?", (total, sale_id))
    conn.commit()
    print(f"Bill created. Total: GHS {total:.2f}")

def view_bills():
    c.execute("SELECT sale_id, sale_date, total_amount FROM sales")
    bills = c.fetchall()
    for bill in bills:
        print(f"\nBill ID: {bill[0]}, Date: {bill[1]}, Total: GHS {bill[2]:.2f}")
        c.execute('''SELECT products.name, bill_items.quantity, bill_items.unit_price, bill_items.total_price
                     FROM bill_items JOIN products ON bill_items.product_id = products.product_id
                     WHERE bill_items.sale_id=?''', (bill[0],))
        items = c.fetchall()
        for item in items:
            print(f"  {item[0]} x{item[1]} @ GHS {item[2]:.2f} = GHS {item[3]:.2f}")
    print()

# --- Main Menu ---
def main():
    while True:
        print("\n--- Chesu Provision Shop Billing System ---")
        print("1. Add Product")
        print("2. Add Customer")
        print("3. List Products")
        print("4. Create Bill")
        print("5. View Bills")
        print("0. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            add_product()
        elif choice == '2':
            add_customer()
        elif choice == '3':
            list_products()
        elif choice == '4':
            create_bill()
        elif choice == '5':
            view_bills()
        elif choice == '0':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
    conn.close()


