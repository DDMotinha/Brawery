from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

import sys
import os
sys.path.append('/opt/airflow')

from src.extractors.brewery_api import extract_breweries
from src.transformers.bronze_to_silver import transform_bronze_to_silver
from src.transformers.silver_to_gold import transform_silver_to_gold
from src.utils.logging_utils import setup_logger

logger = setup_logger()

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'breweries_pipeline',
    default_args=default_args,
    description='A pipeline to extract, transform, and load brewery data',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['breweries', 'data_engineering'],
)

# Define the tasks
extract_task = PythonOperator(
    task_id='extract_breweries',
    python_callable=extract_breweries,
    op_kwargs={
        'output_path': '/opt/airflow/data/bronze/breweries/{{ ds }}/breweries.json',
        'per_page': 50,
        'max_pages': 10,  # Adjust based on API limits and data volume
    },
    dag=dag,
)

bronze_to_silver_task = PythonOperator(
    task_id='bronze_to_silver',
    python_callable=transform_bronze_to_silver,
    op_kwargs={
        'input_path': '/opt/airflow/data/bronze/breweries/{{ ds }}/breweries.json',
        'output_base_path': '/opt/airflow/data/silver/breweries',
        'execution_date': '{{ ds }}',
    },
    dag=dag,
)

silver_to_gold_task = PythonOperator(
    task_id='silver_to_gold',
    python_callable=transform_silver_to_gold,
    op_kwargs={
        'input_base_path': '/opt/airflow/data/silver/breweries',
        'output_path': '/opt/airflow/data/gold/breweries_by_type_location/{{ ds }}/breweries_agg.parquet',
        'execution_date': '{{ ds }}',
    },
    dag=dag,
)

# Create directories if they don't exist
create_dirs_task = BashOperator(
    task_id='create_directories',
    bash_command="""
    mkdir -p /opt/airflow/data/bronze/breweries/{{ ds }}
    mkdir -p /opt/airflow/data/silver/breweries
    mkdir -p /opt/airflow/data/gold/breweries_by_type_location/{{ ds }}
    """,
    dag=dag,
)

# Define the task dependencies
create_dirs_task >> extract_task >> bronze_to_silver_task >> silver_to_gold_task
