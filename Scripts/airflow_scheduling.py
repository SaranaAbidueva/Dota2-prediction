from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess


# Функция для выполнения скрипта
def run_script(script_name):
    """Запускает указанный скрипт."""
    try:
        subprocess.run(['python', script_name], check=True)
        print(f"{script_name} выполнен успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении {script_name}: {e}")


# Параметры по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime(2024, 12, 8),  # Установите дату начала
    'retries': 1,
    'retry_delay': timedelta(days=1),
}

# Создание DAG
dag = DAG(
    'weekly_tasks',
    default_args=default_args,
    description='Weekly tasks to run Python scripts',
    schedule_interval='@weekly',  # Запуск каждую неделю
)

# Определение задач
download_task = PythonOperator(
    task_id='download',
    python_callable=run_script,
    op_kwargs={'script_name': 'Scripts/data_downloading.py'},
    dag=dag,
)

collect_task = PythonOperator(
    task_id='collect',
    python_callable=run_script,
    op_kwargs={'script_name': 'Scripts/data_collecting.py'},
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess',
    python_callable=run_script,
    op_kwargs={'script_name': 'Scripts/data_preprocessing.py'},
    dag=dag,
)

hyperparameters_task = PythonOperator(
    task_id='hyperparameters',
    python_callable=run_script,
    op_kwargs={'script_name': 'Scripts/hyperparameters_tuning.py'},
    dag=dag,
)

train_best_task = PythonOperator(
    task_id='train_best',
    python_callable=run_script,
    op_kwargs={'script_name': 'Scripts/train_best_model.py'},
    dag=dag,
)

# Определение порядка выполнения задач
download_task >> collect_task >> preprocess_task >> hyperparameters_task >> train_best_task

