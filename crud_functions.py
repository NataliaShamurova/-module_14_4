import sqlite3 as sq


def initiate_db():
    db = sq.connect('products')
    cur = db.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INT NOT NULL               
    )
    ''')
    db.commit()
    db.close()

def add_product(product_data):
    conn = sq.connect('products')
    c = conn.cursor()
    c.execute('''INSERT INTO Products (title, description, price) VALUES (?, ?, ?)''', product_data)
    conn.commit()
    conn.close()

def get_all_products():
    db = sq.connect('products')
    cur = db.cursor()
    cur.execute('SELECT * FROM Products')
    products = cur.fetchall()
    db.close()

    return products



