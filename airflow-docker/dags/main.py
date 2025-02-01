import sys
import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Lấy đường dẫn tuyệt đối của thư mục hiện tại chứa DAGs
current_dir = os.path.dirname(os.path.abspath(__file__))

# Di chuyển lên một cấp và thêm đường dẫn đến all_project_2
project_root = os.path.abspath(os.path.join(current_dir, r"D:\DE_project\all_project_2"))

# Thêm đường dẫn thư mục all_project_2 vào sys.path nếu chưa có
if project_root not in sys.path:
    sys.path.append(project_root)

# Kiểm tra lại sys.path
print("Updated sys.path:", sys.path)

# Import các module từ all_project_2

from all_project_2.data_crawl import get_brands, crawl_all_products
from all_project_2.s3_storage import S3Storage
from all_project_2.transform_data import clean_data, transform_data, validate_data
from all_project_2.db_operations import connect_mysql, drop_table_if_exists, create_table, insert_data, close_connection
from all_project_2.langchain_integration import setup_langchain


# Load environment variables from .env file
load_dotenv(os.path.join(project_root, ".env"))

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Định nghĩa DAG
dag = DAG(
    dag_id='data_pipeline_dag',
    default_args=default_args,
    description='DAG xử lý pipeline Hasaki',
    schedule_interval='@daily',  # Chạy hàng ngày
    start_date=datetime(2025, 1, 1),
    catchup=False
)

# 1. Crawl dữ liệu
def crawl_data():
    url = "https://hasaki.vn/thuong-hieu"
    print("Bắt đầu crawl dữ liệu từ website...")
    lst_brand_hasaki = get_brands(url)
    all_products = crawl_all_products(lst_brand_hasaki, delay=1)
    
    df = pd.DataFrame(all_products)
    output_file = os.path.join(project_root, "product_information.csv")
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Dữ liệu sản phẩm đã được lưu vào file {output_file}.")
    return output_file

# 2. Upload dữ liệu lên S3
def upload_to_s3(ti):
    output_file = ti.xcom_pull(task_ids='crawl_data')

    S3_ENDPOINT = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    s3 = S3Storage(endpoint=S3_ENDPOINT, access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY)
    s3.create_bucket(BUCKET_NAME)
    object_name = os.path.basename(output_file)
    s3.upload_file(bucket_name=BUCKET_NAME, object_name=object_name, file_path=output_file)
    print("Upload lên MinIO thành công.")

# 3. Transform dữ liệu
def transform_data_task():
    transformed_file = os.path.join(project_root, "transformed_data.csv")
    df = pd.read_csv(os.path.join(project_root, "product_information.csv"))
    
    df = clean_data(df)
    df = transform_data(df)
    df = validate_data(df)
    
    df.to_csv(transformed_file, index=False, encoding="utf-8")
    print(f"Dữ liệu đã được transform và lưu vào {transformed_file}")
    return transformed_file

# 4. Đưa dữ liệu vào MySQL
def update_mysql(ti):
    transformed_file = ti.xcom_pull(task_ids='transform_data')

    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    connection = connect_mysql(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    table_name = "products"

    df = pd.read_csv(transformed_file)
    drop_table_if_exists(connection, table_name)
    create_table(connection, table_name)
    insert_data(connection, table_name, df)
    close_connection(connection)
    print("Dữ liệu đã được cập nhật vào MySQL.")

# 5. Truy vấn MySQL bằng LangChain
def langchain_query():
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    API_KEY = os.getenv("API_KEY")

    db_chain = setup_langchain(MYSQL_USER, MYSQL_PASSWORD, f"{MYSQL_HOST}:{MYSQL_PORT}", MYSQL_DATABASE, API_KEY)
    query = "Sản phẩm có giá nhỏ nhất là gì? và giá của sản phẩm đó là bao nhiêu?"
    result = db_chain.run(query)

    print("Kết quả truy vấn:")
    print(result)

# Định nghĩa các task trong DAG
t1 = PythonOperator(
    task_id='crawl_data',
    python_callable=crawl_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    provide_context=True,
    dag=dag
)

t3 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data_task,
    dag=dag
)

t4 = PythonOperator(
    task_id='update_mysql',
    python_callable=update_mysql,
    provide_context=True,
    dag=dag
)

t5 = PythonOperator(
    task_id='langchain_query',
    python_callable=langchain_query,
    dag=dag
)

# Xác định luồng chạy DAG
t1 >> t2 >> t3 >> t4 >> t5
