from data_crawl import get_brands, crawl_all_products
from s3_storage import S3Storage
from transform_data import clean_data, transform_data, validate_data
from db_operations import connect_mysql, drop_table_if_exists, create_table, insert_data, close_connection
from langchain_integration import setup_langchain
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    # URL chính để lấy danh sách các thương hiệu
    url = "https://hasaki.vn/thuong-hieu"

    # 1. Crawl dữ liệu
    print("Bắt đầu crawl dữ liệu từ website...")
    lst_brand_hasaki = get_brands(url)
    print(f"Đã lấy được {len(lst_brand_hasaki)} thương hiệu.")

    all_products = crawl_all_products(lst_brand_hasaki, delay=1)

    df = pd.DataFrame(all_products)
    output_file = "product_information.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dữ liệu sản phẩm đã được lưu vào file {output_file}.")

    # 2. Kết nối MinIO và upload file
    print("Kết nối đến MinIO và upload file...")

    S3_ENDPOINT = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    s3 = S3Storage(endpoint=S3_ENDPOINT, access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY)
    s3.create_bucket(BUCKET_NAME)
    object_name = os.path.basename(output_file)
    s3.upload_file(bucket_name=BUCKET_NAME, object_name=object_name, file_path=output_file)

    # 3. Transform dữ liệu
    print("Tải dữ liệu từ MinIO để transform...")
    temp_local_path = f"transformed_{output_file}"
    s3.client.fget_object(BUCKET_NAME, object_name, temp_local_path)

    df = pd.read_csv(temp_local_path)
    df = clean_data(df)
    df = transform_data(df)
    df = validate_data(df)

    transformed_file = "transformed_data.csv"
    df.to_csv(transformed_file, index=False, encoding="utf-8")
    s3.upload_file(bucket_name=BUCKET_NAME, object_name=transformed_file, file_path=transformed_file)

    # 4. Đưa dữ liệu vào MySQL
    print("Kết nối MySQL và cập nhật dữ liệu...")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    connection = connect_mysql(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    table_name = "products"

    drop_table_if_exists(connection, table_name)
    create_table(connection, table_name)
    insert_data(connection, table_name, df)
    close_connection(connection)

    print("Dữ liệu đã được cập nhật vào MySQL.")

    # 5. Tích hợp LangChain để truy vấn MySQL
    print("Tích hợp LangChain và truy vấn cơ sở dữ liệu...")
    API_KEY = os.getenv("API_KEY")
    db_chain = setup_langchain(MYSQL_USER, MYSQL_PASSWORD, f"{MYSQL_HOST}:{MYSQL_PORT}", MYSQL_DATABASE, API_KEY)

    query = "Sản phẩm có giá nhỏ nhất là gì? và giá của sản phẩm đó là bao nhiêu?"  # Truy vấn mẫu
    result = db_chain.run(query)

    print("Kết quả truy vấn:")
    print(result)

    print("Quá trình hoàn tất!")
