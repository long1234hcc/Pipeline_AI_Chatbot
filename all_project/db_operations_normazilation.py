import mysql.connector
from mysql.connector import Error
import pandas as pd

def connect_mysql(host, port, user, password, database):
    """
    Kết nối đến MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print(f"Kết nối thành công tới database '{database}'!")
        return connection
    except Error as e:
        print(f"Lỗi khi kết nối MySQL: {e}")
        raise

def drop_table_if_exists(connection, table_name):
    """
    Xoá bảng trong MySQL nếu bảng đã tồn tại.
    """
    try:
        cursor = connection.cursor()
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_query)
        print(f"Bảng '{table_name}' đã được xoá (nếu tồn tại).")
    except Error as e:
        print(f"Lỗi khi xoá bảng: {e}")
        raise

def create_tables(connection):
    """
    Tạo các bảng theo chuẩn hóa 3NF.
    """
    try:
        cursor = connection.cursor()
        
        # Bảng lưu thông tin sản phẩm
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            vn_name VARCHAR(255) NOT NULL,
            en_name VARCHAR(255) NOT NULL,
            url_thumbnail VARCHAR(500)
        );
        """
        cursor.execute(create_products_table)
        
        # Bảng lưu giá sản phẩm (có lịch sử giá)
        create_product_prices_table = """
        CREATE TABLE IF NOT EXISTS product_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            new_price FLOAT NOT NULL,
            old_price FLOAT,
            discount_percentage FLOAT,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_product_prices_table)
        
        # Bảng lưu số lượng bán sản phẩm theo thời gian
        create_sales_table = """
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            sold INT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_sales_table)

        print("Tất cả các bảng đã được tạo thành công!")
    
    except Error as e:
        print(f"Lỗi khi tạo bảng: {e}")
        raise

def insert_product(connection, vn_name, en_name, url_thumbnail):
    """
    Thêm sản phẩm vào bảng 'products' nếu chưa tồn tại.
    """
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO products (vn_name, en_name, url_thumbnail)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE url_thumbnail = VALUES(url_thumbnail);
        """
        cursor.execute(insert_query, (vn_name, en_name, url_thumbnail))
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Lỗi khi chèn sản phẩm: {e}")
        raise

def insert_product_price(connection, product_id, new_price, old_price, discount_percentage):
    """
    Thêm thông tin giá vào bảng 'product_prices'.
    """
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO product_prices (product_id, new_price, old_price, discount_percentage)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (product_id, new_price, old_price, discount_percentage))
        connection.commit()
    except Error as e:
        print(f"Lỗi khi chèn giá sản phẩm: {e}")
        raise

def insert_sales(connection, product_id, sold):
    """
    Thêm số lượng sản phẩm đã bán vào bảng 'sales'.
    """
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO sales (product_id, sold)
        VALUES (%s, %s);
        """
        cursor.execute(insert_query, (product_id, sold))
        connection.commit()
    except Error as e:
        print(f"Lỗi khi chèn số lượng bán: {e}")
        raise

def insert_data(connection, dataframe):
    """
    Chèn dữ liệu từ pandas DataFrame vào MySQL.
    """
    try:
        for _, row in dataframe.iterrows():
            # Chèn sản phẩm vào bảng 'products'
            product_id = insert_product(connection, row['vn_name'], row['en_name'], row['url_thumbnail'])

            # Chèn giá sản phẩm vào bảng 'product_prices'
            insert_product_price(connection, product_id, row['new_price'], row['old_price'], row['discount_percentage'])

            # Chèn số lượng bán vào bảng 'sales'
            insert_sales(connection, product_id, row['sold'])

        print(f"Đã chèn {len(dataframe)} dòng vào database!")
    except Error as e:
        print(f"Lỗi khi chèn dữ liệu vào database: {e}")
        connection.rollback()
        raise

def close_connection(connection):
    """
    Đóng kết nối MySQL.
    """
    if connection.is_connected():
        connection.close()
        print("Kết nối tới MySQL đã được đóng.")
