from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow import BashOperator

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="demo", start_date=datetime(2025, 9, 3), schedule_interval="0 0 * * *", catchup=False) as dag:

    # Tasks are represented as operators
    hello = BashOperator(task_id="hello", bash_command="echo hello")

    @task()
    def airflow_task():
        print("airflow")

    # Set dependencies between tasks
    hello >> airflow_task()


# from airflow.models import DagBag

# def test_dag_loaded():
#     dag_bag = DagBag()
#     dag = dag_bag.get_dag(dag_id="demo")
#     assert dag is not None
#     assert dag.dag_id == "demo"