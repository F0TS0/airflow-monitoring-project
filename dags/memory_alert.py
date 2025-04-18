from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import smtplib
from email.message import EmailMessage
import psutil

def send_alert_email(mem_mb):
    threshold = 50  
    msg = EmailMessage()
    msg.set_content(f"Airflow memory usage is high!\n\nCurrent usage: {mem_mb:.2f} MB\nThreshold: {threshold} MB")
    msg['Subject'] = f'Airflow Memory Alert ({mem_mb:.2f} MB)'
    msg['From'] = 'airflow@example.com'
    msg['To'] = 'test@localhost'

    try:
        with smtplib.SMTP('smtp4dev', 25, timeout=10) as smtp:
            smtp.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"[DAG] Failed to send email: {e}")

def check_memory_usage():
    print("[DAG] Starting memory check...")
    process = psutil.Process()
    mem_mb = process.memory_info().rss / 1024 / 1024
    threshold = 50

    print(f"[DAG] Current memory usage: {mem_mb:.2f} MB | Threshold: {threshold} MB")
    if mem_mb > threshold:
        print("[DAG] Memory over threshold – proceeding to send email.")
        send_alert_email(mem_mb)
        return 'send_email'
    else:
        print("[DAG] Memory within safe limits – skipping email.")
        return 'do_nothing'

with DAG(
    dag_id='memory_alert_email_dag',
    start_date=datetime(2023, 1, 1),
    schedule_interval='* * * * *',
    catchup=False,
    tags=["alert", "memory"]
) as dag:
    check_memory = BranchPythonOperator(
        task_id='check_memory',
        python_callable=check_memory_usage
    )

    send_email = DummyOperator(task_id='send_email')

    do_nothing = DummyOperator(task_id='do_nothing')

    check_memory >> [send_email, do_nothing]