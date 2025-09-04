from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define your Python functions
def run_script_1():
    # Logic for your first script
    print("Running script 1...")

def run_script_2():
    # Logic for your second script
    print("Running script 2...")

def run_script_3():
    # Logic for your third script
    print("Running script 3...")

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id='my_parallel_dag',
    default_args=default_args,
    description='A simple parallel DAG',
    schedule_interval='@daily',  # Run every 24 hours
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Define tasks
    task_1 = PythonOperator(
        task_id='run_script_1',
        python_callable=run_script_1,
    )

    task_2 = PythonOperator(
        task_id='run_script_2',
        python_callable=run_script_2,
    )

    task_3 = PythonOperator(
        task_id='run_script_3',
        python_callable=run_script_3,
    )

    # Set task dependencies
    task_1 >> task_3
    task_2 >> task_3

