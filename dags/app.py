"""Airflow orchestration layer for the Amazon books ETL pipeline."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from amazon_books_pipeline.config import BOOK_LIMIT, POSTGRES_CONN_ID
from amazon_books_pipeline.extract import extract_book_data
from amazon_books_pipeline.load import load_book_data
from amazon_books_pipeline.sql_queries import (
    CREATE_ANALYTICS_VIEWS_SQL,
    CREATE_BOOKS_TABLE_SQL,
    DATA_QUALITY_SQL,
)
from amazon_books_pipeline.transform import transform_book_data


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 6, 20),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="fetch_and_store_amazon_books",
    default_args=default_args,
    description="Fetch Amazon book search data, clean it, and store it in Postgres",
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=["etl", "amazon", "books", "postgres"],
) as dag:
    extract_book_data_task = PythonOperator(
        task_id="extract_book_data",
        python_callable=extract_book_data,
        op_args=[BOOK_LIMIT],
    )

    transform_book_data_task = PythonOperator(
        task_id="transform_book_data",
        python_callable=transform_book_data,
    )

    create_table_task = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id=POSTGRES_CONN_ID,
        sql=CREATE_BOOKS_TABLE_SQL,
    )

    load_book_data_task = PythonOperator(
        task_id="load_book_data",
        python_callable=load_book_data,
    )

    data_quality_check_task = SQLExecuteQueryOperator(
        task_id="data_quality_check",
        conn_id=POSTGRES_CONN_ID,
        sql=DATA_QUALITY_SQL,
    )

    create_analytics_views_task = SQLExecuteQueryOperator(
        task_id="create_analytics_views",
        conn_id=POSTGRES_CONN_ID,
        sql=CREATE_ANALYTICS_VIEWS_SQL,
    )

    extract_book_data_task >> transform_book_data_task >> create_table_task
    create_table_task >> load_book_data_task >> data_quality_check_task >> create_analytics_views_task
