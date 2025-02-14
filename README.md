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

