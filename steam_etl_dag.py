from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 8, 21),
    'retries': 1,
}

def log_start():
    logging.info("Starting Steam ETL pipeline...")

def log_end():
    logging.info("Steam ETL pipeline completed successfully!")

with DAG(
    dag_id='steam_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for processing Steam data',
    start_date=datetime(2025, 8, 21, 8, 28),  # fixed start datetime
    schedule_interval='0 0 * * *',  # daily at midnight
    catchup=False,
    tags=['steam', 'etl'],
) as dag:

    start_log = PythonOperator(
        task_id='log_start',
        python_callable=log_start
    )

    task_01 = BashOperator(
        task_id='extract_app_ids',
        bash_command='python ./steam_data_etl/01_Extract_Steam_AppIDs_To_JSON.py'
    )

    task_02 = BashOperator(
        task_id='extract_valid_app_data',
        bash_command='python ./steam_data_etl/02_Extract_Valid_Steam_AppData_To_JSON.py'
    )

    task_03 = BashOperator(
        task_id='transform_data_to_csv',
        bash_command='python ./steam_data_etl/03_Transform_Steam_App_Data_to_CSV.py'
    )

    task_04 = BashOperator(
        task_id='load_to_staging_step1',
        bash_command='python ./steam_data_etl/04_Load_CSV_to_Steam_Staging_Table.py'
    )

    task_05 = BashOperator(
        task_id='load_to_staging_step2',
        bash_command='python ./steam_data_etl/05_Load_CSV_to_Steam_Staging_Table.py'
    )

    task_06 = BashOperator(
        task_id='load_to_fact_dim_tables',
        bash_command='python ./steam_data_etl/06_Load_Staging_To_Fact_Dim_Tables.py'
    )

    end_log = PythonOperator(
        task_id='log_end',
        python_callable=log_end
    )

    # Define the order of execution
    start_log >> task_01 >> task_02 >> task_03 >> task_04 >> task_05 >> task_06 >> end_log
