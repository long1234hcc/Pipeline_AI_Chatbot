from datetime import timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

# Các cấu hình cơ bản của DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflowadmin@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Tạo một DAG
dag = DAG(
    'hello_world_2',
    default_args=default_args,
    description='A simple tutorial DAG 2',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=['example'],
)

# Tạo tasks
t1 = DummyOperator(
    task_id='start',
    dag=dag,
)

t2 = DummyOperator(
    task_id='end',
    dag=dag,
)

# Định nghĩa thứ tự thực hiện task
t1 >> t2
