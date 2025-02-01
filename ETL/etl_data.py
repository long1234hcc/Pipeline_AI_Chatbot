import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import pandas as pd  # Thêm thư viện pandas

# URL của trang web bạn muốn lấy HTML
url = r"https://hasaki.vn/thuong-hieu" # Thay bằng URL của trang bạn đang xem

lst_brand_hasaki = []


# Gửi yêu cầu GET để lấy nội dung trang web
response = requests.get(url)

# Kiểm tra nếu yêu cầu thành công
if response.status_code == 200:
    # Lấy nội dung HTML
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")
    # Tìm tất cả các thẻ <a> có thuộc tính href
    links = soup.find_all('a', href=True)

    # Lấy giá trị của href từ các thẻ <a>
    hrefs = [link['href'] for link in links]
    hrefs = [url_brand for url_brand in hrefs if url_brand.startswith("/thuong-hieu")]
    hrefs = set(hrefs)

    # In ra kết quả
    for href in hrefs:
        lst_brand_hasaki.append(f"https://hasaki.vn/{href}")

else:
    print(f"Không thể truy cập trang web. Status code: {response.status_code}")
    
   
## Transform to dataframe pandas 

all_products = []

def extract_information_product(product_url):
    lst_info_product = []
    response = requests.get(product_url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Tìm tất cả các phần tử có class là "ProductGridItem__itemOuter"
        items = soup.find_all("div", class_="ProductGridItem__itemOuter")
        
        # Duyệt qua từng phần tử và lấy thông tin cụ thể
        for item in items:
            dict_info_product = {}
            
            # Lấy giá mới
            dict_info_product["new_price"] = item.find("strong", class_="item_giamoi txt_16").text.strip() if item.find("strong", class_="item_giamoi txt_16") else None
            
            # Lấy giá cũ
            dict_info_product["old_price"] = item.find("span", class_="item_giacu txt_12 right").text.strip() if item.find("span", class_="item_giacu txt_12 right") else None
            
            # Lấy giảm giá
            dict_info_product["discount"] = item.find("span", class_="discount_percent2_deal").text.strip() if item.find("span", class_="discount_percent2_deal") else None
            
            # Lấy số lượng đã bán
            sold_info = item.find("span", class_="item_count_by")
            dict_info_product["sold"] = sold_info.text.strip() if sold_info else None
            
            # Lấy tên sản phẩm tiếng Việt
            vn_name = item.find("div", class_="vn_names")
            dict_info_product["vn_name"] = vn_name.text.strip() if vn_name else None
            
            # Lấy tên sản phẩm tiếng Anh
            en_name = item.find("div", class_="en_names")
            dict_info_product["en_name"] = en_name.text.strip() if en_name else None
            
            ## Link hình ảnh
            img_tag = item.find("img", class_="img_thumb lazy")
            if img_tag and img_tag.get("data-src"):
                dict_info_product["url_thumbnail"] = img_tag["data-src"]
            else:
                dict_info_product["url_thumbnail"] = None
            
            # Thêm vào danh sách sản phẩm
            lst_info_product.append(dict_info_product)
    
    return lst_info_product

# Duyệt qua các trang thương hiệu và thu thập thông tin sản phẩm
for brand in tqdm(lst_brand_hasaki[:10], desc="Duyệt qua các thương hiệu", total=len(lst_brand_hasaki[:5])):
    lst_product = extract_information_product(brand)
    all_products.extend(lst_product)
    print(f"Đã lấy thông tin sản phẩm từ {brand}")
    time.sleep(1)

# Tạo DataFrame từ dữ liệu thu thập được
df = pd.DataFrame(all_products)




## Connect to Minio S3

from minio import Minio
from minio.error import S3Error

# Cấu hình thông tin kết nối MinIO
minio_client = Minio(
    "localhost:9000",  # Địa chỉ server MinIO (localhost vì chạy trên máy bạn)
    access_key="admin",  # Username (đặt khi chạy container)
    secret_key="admin123",  # Password (đặt khi chạy container)
    secure=False  # MinIO không sử dụng HTTPS trong môi trường cục bộ
)

try:
    buckets = minio_client.list_buckets()
    print("Danh sách buckets:")
    for bucket in buckets:
        print(f"- {bucket.name} (created: {bucket.creation_date})")
except S3Error as e:
    print("Lỗi khi kết nối MinIO:", e)
    
    
### Tạo bucket
bucket_name = "hasaki"  # Tên bucket mới

# Kiểm tra và tạo bucket nếu chưa tồn tại
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' đã được tạo.")
else:
    print(f"Bucket '{bucket_name}' đã tồn tại.")


## Đưa file vừa crawl được vào bucket

file_path = r"C:\Users\ADMIN\Downloads\hasaki_products.csv"  
object_name = "hasaki_products.csv"  # Tên file khi lưu trong MinIO

minio_client.fput_object(bucket_name, object_name, file_path)
print(f"File '{file_path}' đã được upload vào bucket '{bucket_name}' với tên '{object_name}'.")


## Connect MySQL
import mysql.connector
from mysql.connector import Error

try:
    # Kết nối tới MySQL server
    connection = mysql.connector.connect(
        host='127.0.0.1',         # Địa chỉ host (localhost hoặc 127.0.0.1)
        port=3307,                # Cổng đã ánh xạ (3307 trong lệnh Docker)
        user='admin',             # Tên người dùng (admin)
        password='admin123',      # Mật khẩu người dùng (admin123)
        database='my_database'    # Tên database (my_database)
    )

    if connection.is_connected():
        print("Kết nối thành công tới database 'my_database'!")

        # Thực hiện một truy vấn kiểm tra
        cursor = connection.cursor()
        # cursor.execute("SELECT DATABASE();")
        # current_db = cursor.fetchone()
        # print("Đang làm việc với database:", current_db[0])
        
        
        
        ## Check  table
        # Lấy danh sách các bảng
        # cursor.execute("SHOW TABLES;")
        # tables = cursor.fetchall()

        # print("Danh sách các bảng trong database:")
        # for table in tables:
        #     print(table[0])
            
            
        ## Kiểm tra thông tin trong 1 bảng
        # Xem cấu trúc bảng cụ thể
        # table_name = 'your_table_name'  # Thay bằng tên bảng cần kiểm tra
        # cursor.execute(f"DESCRIBE {table_name};")
        # columns = cursor.fetchall()

        # print(f"Cấu trúc bảng '{table_name}':")
        # for column in columns:
        #     print(column)



except Error as e:
    print("Lỗi khi kết nối MySQL:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Kết nối tới MySQL đã được đóng.")



import pandas as pd
import mysql.connector
from mysql.connector import Error

# 1. Đọc file CSV
file_path = r"C:\Users\ADMIN\Downloads\hasaki_products.csv"  # Đường dẫn tới file CSV
data = pd.read_csv(file_path)


#2. Transform Data
import re

def extract_numbers(input_string):
    # Kiểm tra xem chuỗi có phải là số hay không
    try:
        # Nếu input là số, chuyển nó thành số thực
        return float(input_string)
    except ValueError:
        # Nếu không, bỏ dấu phẩy và chấm, sau đó sử dụng regex để tìm tất cả các chuỗi số
        clean_string = input_string.replace(".", "").replace(",", "")
        numbers = re.findall(r'\d+', clean_string)
        # Chuyển đổi kết quả tìm được thành số nguyên và lấy số đầu tiên
        return float(numbers[0]) if numbers else None

## Fillna
data['new_price'] = data['new_price'].fillna(0)
data['old_price'] = data['old_price'].fillna(0)
data['sold'] = data['sold'].fillna(0)

##Transform
data['new_price'] = data['new_price'].apply(extract_numbers)
data['old_price'] = data['old_price'].apply(extract_numbers)
data['sold'] = data['sold'].apply(extract_numbers)


## Inseart Data

import mysql.connector
from mysql.connector import Error
import pandas as pd  # Đảm bảo rằng bạn đã nhập thư viện này

# 2. Kết nối tới database
try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,  # Cổng đã ánh xạ
        user='admin',  # Tên người dùng MySQL
        password='admin123',  # Mật khẩu
        database='my_database'  # Tên database
    )

    if connection.is_connected():
        print("Kết nối thành công tới database!")

        # 3. Kiểm tra và tạo bảng nếu chưa tồn tại
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                name VARCHAR(255),
                new_price FLOAT,
                old_price FLOAT,
                discount VARCHAR(50),
                sold INT,
                url_thumbnail VARCHAR(500)
            );
        """)
        print("Bảng 'users' đã sẵn sàng!")

        # 4. Chuẩn bị dữ liệu để upload
        for _, row in data.iterrows():
            try:
                # Kiểm tra và thay thế NaN bằng None (NULL trong SQL)
                values = (
                    row['id'],
                    row['product_name'] if pd.notna(row['product_name']) else None,
                    row['new_price'] if pd.notna(row['new_price']) else None,
                    row['old_price'] if pd.notna(row['old_price']) else None,
                    row['discount'] if pd.notna(row['discount']) else None,
                    row['sold'] if pd.notna(row['sold']) else None,
                    row['url_thumbnail'] if pd.notna(row['url_thumbnail']) else None
                )
                sql = """
                    INSERT INTO users (id, name, new_price, old_price, discount, sold, url_thumbnail) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    name=VALUES(name), 
                    new_price=VALUES(new_price),
                    old_price=VALUES(old_price),
                    discount=VALUES(discount),
                    sold=VALUES(sold),
                    url_thumbnail=VALUES(url_thumbnail);
                """
                cursor.execute(sql, values)
            except Error as e:
                print(f"Lỗi khi thêm dữ liệu cho id {row['id']}: {e}")

        # 5. Lưu các thay đổi
        connection.commit()
        print("Dữ liệu đã được upload thành công!")

except Error as e:
    print("Lỗi khi kết nối hoặc thao tác với MySQL:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Kết nối tới MySQL đã được đóng.")



### Sử dụng langchain để kết nối MySQL


## Setup LLM Model
import os
import google.generativeai as genai
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
import mysql.connector
from mysql.connector import Error
import pandas as pd


key_2 = "AIzaSyBIj3oASm62pVvfxC0YtQ7wteUZsEddjtk"
API_KEY = key_2 
genai.configure(api_key=API_KEY)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat()

response = chat_session.send_message("chào bạn")



## Connect My SQL 
db_user = "admin"
db_password = "admin123"
db_host = "localhost:3307" 
db_name = "my_database"

db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=3)



## Wrap
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from typing import Any, Optional, List
from pydantic import Field

class ChatSessionWrapper(LLM):
    chat_session: Any = Field(...)  # Định nghĩa thuộc tính bắt buộc với Pydantic

    def __init__(self, chat_session: Any, **kwargs):
        """
        Khởi tạo lớp wrapper với một chat_session từ Google Generative AI.
        """
        super().__init__(chat_session=chat_session, **kwargs)

    @property
    def _llm_type(self) -> str:
        """
        Xác định loại LLM để LangChain nhận diện.
        """
        return "custom_google_chat_session"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Triển khai phương thức _call để sử dụng với LangChain.
        """
        response = self.chat_session.send_message(prompt)
        return response.text

    def generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs) -> LLMResult:
        """
        Triển khai phương thức generate để trả về LLMResult, hỗ trợ LangChain.
        """
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop)
            generations.append([Generation(text=response)])  # Mỗi prompt sinh một danh sách Generation

        # Trả về đối tượng LLMResult
        return LLMResult(generations=generations)


# Kiểm tra chat_session hoạt động
response = chat_session.send_message("Chào bạn")
print(response.text)

# Tạo instance của ChatSessionWrapper
llm = ChatSessionWrapper(chat_session=chat_session)

# Đảm bảo rằng thuộc tính chat_session tồn tại
print(llm.chat_session)  # Kiểm tra xem thuộc tính được gán đúng


## Query

# Tích hợp với SQLDatabaseChain
db_chain = SQLDatabaseChain.from_llm(llm,db, verbose=True)

# Chạy truy vấn SQL
query = "có bao nhiêu dòng trong data"  # Thay thế bằng truy vấn của bạn
result = db_chain.run(query)

print("Kết quả truy vấn:")
print(result)





    

