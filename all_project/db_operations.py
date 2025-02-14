import mysql.connector
from mysql.connector import Error
import pandas as pd

def connect_mysql(host, port, user, password, database):
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
    try:
        cursor = connection.cursor()
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_query)
        print(f"Bảng '{table_name}' đã được xoá (nếu tồn tại).")
    except Error as e:
        print(f"Lỗi khi xoá bảng: {e}")
        raise


def create_table(connection, table_name):
    try:
        cursor = connection.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            vn_name VARCHAR(255),
            en_name VARCHAR(255),
            new_price FLOAT,
            old_price FLOAT,
            discount_percentage FLOAT,
            sold INT,
            url_thumbnail VARCHAR(500)
        );
        """
        cursor.execute(create_table_query)
        print(f"Bảng '{table_name}' đã sẵn sàng!")
    except Error as e:
        print(f"Lỗi khi tạo bảng: {e}")
        raise

def insert_data(connection, table_name, dataframe):
    try:
        cursor = connection.cursor()
        insert_query = f"""
        INSERT INTO {table_name} (vn_name, en_name, new_price, old_price, discount_percentage, sold, url_thumbnail)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        new_price = VALUES(new_price),
        old_price = VALUES(old_price),
        discount_percentage = VALUES(discount_percentage),
        sold = VALUES(sold),
        url_thumbnail = VALUES(url_thumbnail);
        """
        data_to_insert = [
            (
                row['vn_name'],
                row['en_name'],
                row['new_price'],
                row['old_price'],
                row['discount_percentage'],
                row['sold'],
                row['url_thumbnail']
            )
            for _, row in dataframe.iterrows()
        ]

        cursor.executemany(insert_query, data_to_insert)
        connection.commit()
        print(f"Đã chèn {cursor.rowcount} dòng vào bảng '{table_name}'!")
    except Error as e:
        print(f"Lỗi khi chèn dữ liệu vào bảng '{table_name}': {e}")
        connection.rollback()
        raise

def close_connection(connection):

    if connection.is_connected():
        connection.close()
        print("Kết nối tới MySQL đã được đóng.")
