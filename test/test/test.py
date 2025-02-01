import sys
import os
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Lấy đường dẫn tuyệt đối của thư mục hiện tại chứa DAGs
current_dir = os.path.dirname(os.path.abspath(__file__))

# Di chuyển lên một cấp từ thư mục hiện tại của file này, sau đó truy cập vào thư mục all_project_2
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', 'all_project_2'))

# Thêm đường dẫn thư mục all_project_2 vào sys.path nếu chưa có
if project_root not in sys.path:
    sys.path.append(project_root)

# Kiểm tra lại sys.path
print("Updated sys.path:", sys.path)

# Import các module từ all_project_2
from data_crawl import get_brands, crawl_all_products
from s3_storage import S3Storage
from transform_data import clean_data, transform_data, validate_data
from db_operations import connect_mysql, drop_table_if_exists, create_table, insert_data, close_connection
from langchain_integration import setup_langchain

# Thử nghiệm các hàm từ data_crawl
print("Testing get_brands function:")
try:
    brands = get_brands()
    print("Brands:", brands)
except Exception as e:
    print("Error occurred while getting brands:", e)

print("Testing crawl_all_products function:")
try:
    products = crawl_all_products()
    print("Products:", products)
except Exception as e:
    print("Error occurred while crawling products:", e)
