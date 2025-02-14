# Tên dự án: Dự án chatbot hỏi đáp cơ sở dữ liệu bán hàng
## Mục đích dự án: Tự động trả ra các kết quả thống kê về cơ sở dữ liệu bán hàng ngày (Sản phẩm nào bán chạy hôm nay?, Doanh số hàng ngày?,....)
## Mô tả dự án: 
1. Crawl data các dữ liệu của website ecom
2. Lưu trữ các file tại DataLake (Minio S3)
3. Chuyển đổi dữ liệu và đưa vào DataWarehouse (MySQL)
4. Xây dựng chatbot bằng Langchain và Google API key (Gemini-flask-1.5)
5. Query cơ sở dữ liệu để trả ra các kết quả thống kê

## Các bước vận hành dự án
1. Cài MySQL, MinioS3, Airflow bằng docker
2. Viết file docker-compose.yaml
3. Chạy airflow trên port localhost:8080
4. Đưa dự án vào folder dags trong folder chứa airflow
5. Quản lý dự án và chạy tự động trên giao diện của airflow


## Mở rộng dự án
Xây dựng tự động báo cáo bằng Power BI hoặc Tableu để lên báo cáo tự động hàng ngày


# Project Name: Sales Database Q&A Chatbot Project
## Project Purpose: Automate the generation of statistical results from the daily sales database (e.g., Which product sold the most today? What is the daily revenue? etc.).

## Project Description:
1. Crawl data from the e-commerce website.
2. Store files in DataLake (Minio S3).
3. Transform data and load it into DataWarehouse (MySQL).
4. Build a chatbot using LangChain and Google API key (Gemini-flask-1.5).
5. Query the database to generate statistical reports.
   
## Project Operation Steps:
1. Install MySQL, Minio S3, and Airflow using Docker.
2. Write the docker-compose.yaml file.
3. Run Airflow on localhost:8080.
4. Place the project into the dags folder inside the Airflow directory.
5. Manage and automate the project through the Airflow interface.
   
Project Expansion:
Develop automated reporting using Power BI or Tableau for daily reports.

