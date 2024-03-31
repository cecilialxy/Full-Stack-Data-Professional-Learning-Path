from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

default_args = {
    'owner': 'DataEngineeringTea',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email': ['data_engineer@YourSquaremetergardening.com'],
    'email_on_failure': TRUE,
    'email_on_retry': TRUE,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weekly_kpi_report',
    default_args=default_args,
    description='Data Pipeline for Sqaure Meter Gardening project weekly KPI report',
    schedule_interval='59 23 * * 0',  # Run at 12 PM every Sunday
    catchup=False,
)

def fetch_data():
    # Connect to PostgreSQL database and fetch data
    conn = psycopg2.connect(
        dbname="gardening_commerce_db",
        user="dataengineerteam",
        password="your_email_password",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute(open('fetch_data.sql', 'r').read())
    records = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(records, columns=columns)
    conn.close()
    return df

def calculate_kpis(df):
    # Calculate KPIs: Volume of Transactions, Average Order Value, Average Basket Size
    volume_of_transactions = len(df)
    average_order_value = df['TotalAmount'].mean()
    average_basket_size = df.groupby('OrderID')['ProductId'].count().mean()
    # Generate the KPI report
    report = f"Weekly KPI Report:\nVolume of Transactions: {volume_of_transactions}\nAverage Order Value: {average_order_value}\nBasket Size: {average_basket_size}"
    print(report)
    return volume_of_transactions, average_order_value, average_basket_size

    
# Task to extract data from source systems
fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
        dag=dag,
    )

calculate_kpis_task = PythonOperator(
        task_id='calculate_kpis',
        python_callable=calculate_kpis,
        op_args=[fetch_data_task.output],
        dag=dag,
    )

# Define task dependencies
fetch_data_task >> calculate_kpis_task
