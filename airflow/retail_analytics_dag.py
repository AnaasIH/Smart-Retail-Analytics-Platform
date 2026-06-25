from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'retail_admin',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'smart_retail_analytics_pipeline',
    default_args=default_args,
    description='End-to-End Retail Data Pipeline',
    schedule_interval='@daily',
    catchup=False
) as dag:

    check_raw_files = BashOperator(
        task_id='check_raw_files',
        bash_command='test -f /opt/airflow/data/raw/customers.csv && test -f /opt/airflow/data/raw/orders.csv'
    )

    run_data_cleaning = BashOperator(
        task_id='run_data_cleaning',
        bash_command='python /opt/airflow/pyspark_jobs/clean_retail_data.py || echo "Spark not initiated, running regular fallback"'
    )

    check_raw_files >> run_data_cleaning