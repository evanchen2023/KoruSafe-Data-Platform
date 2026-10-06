import os  # 读取环境变量，用来配置数据库和项目路径
import sys  # 修改 Python import 搜索路径，让 Airflow 找到本地 ingestion package
from datetime import datetime, timedelta  # 设置 DAG 开始时间和重试间隔
from pathlib import Path  # 用更稳定的方式处理文件路径

import psycopg2  # 用来测试 PostgreSQL 连接
from airflow import DAG  # Airflow DAG 主对象
from airflow.exceptions import AirflowException  # 在 DAG 解析阶段抛出清晰错误
from airflow.providers.standard.operators.python import PythonOperator  # 用 Python 函数作为 Airflow task


POSTGRES_HOST = os.getenv("KORUSAFE_POSTGRES_HOST", "korusafe-postgres")  # Airflow 容器里访问业务 PostgreSQL 的服务名
POSTGRES_PORT = int(os.getenv("KORUSAFE_POSTGRES_PORT", "5432"))  # PostgreSQL 默认端口
POSTGRES_DB = os.getenv("KORUSAFE_POSTGRES_DB", "korusafe")  # 业务数据库名称
POSTGRES_USER = os.getenv("KORUSAFE_POSTGRES_USER", "postgres")  # 业务数据库用户名
POSTGRES_PASSWORD = os.getenv("KORUSAFE_POSTGRES_PASSWORD", "postgres")  # 业务数据库密码

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)  # SQLAlchemy 使用的数据库连接字符串
os.environ.setdefault("DATABASE_URL", DATABASE_URL)  # 必须在 import ingestion.load_to_postgres 之前设置


def add_project_root_to_python_path():
    """Allow this Airflow DAG to import the project's local ingestion package."""
    dag_dir = Path(__file__).resolve().parent  # 当前 DAG 文件所在目录

    candidate_roots = [
        Path(os.getenv("KORUSAFE_PROJECT_ROOT", "")),  # Docker Compose 推荐传入的项目根目录
        dag_dir.parent,  # 本地运行时，dags 的上一层通常就是项目根目录
        Path("/opt/airflow/project"),  # Airflow Docker 容器中的项目挂载路径
    ]  # 依次尝试这些可能的项目根目录

    for project_root in candidate_roots:
        if not project_root:
            continue  # 跳过空路径

        ingestion_dir = project_root / "ingestion"  # ingestion package 应该存在于项目根目录下
        if ingestion_dir.exists():
            project_root_text = str(project_root)  # sys.path 需要字符串路径
            if project_root_text not in sys.path:
                sys.path.insert(0, project_root_text)  # 把项目根目录加入 Python import 搜索路径
            return project_root  # 找到正确项目根目录后返回

    raise AirflowException(
        "Cannot find the KoruSafe project root. "
        "Set KORUSAFE_PROJECT_ROOT or mount the project into the Airflow container."
    )  # 如果 Airflow 找不到 ingestion，就让 DAG 明确失败


PROJECT_ROOT = add_project_root_to_python_path()  # 初始化项目根目录，并确保 Python 能 import ingestion

from ingestion.extract import extract_all  # noqa: E402  # 使用项目已有的 extract 逻辑
from ingestion.load_to_postgres import load_all  # noqa: E402  # 使用项目已有的 PostgreSQL load 逻辑
from ingestion.transform import transform_all  # noqa: E402  # 使用项目已有的 transform 逻辑
from ingestion.validate import validate_all  # noqa: E402  # 使用项目已有的数据质量验证逻辑


def check_postgres_connection():
    print("Checking KoruSafe PostgreSQL connection...")  # 这个 task 专门检查数据库是否可连接

    with psycopg2.connect(
        host=POSTGRES_HOST,  # 数据库 host
        port=POSTGRES_PORT,  # 数据库 port
        database=POSTGRES_DB,  # 数据库名称
        user=POSTGRES_USER,  # 数据库用户
        password=POSTGRES_PASSWORD,  # 数据库密码
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")  # 最小 SQL 查询，用来确认连接有效
            result = cursor.fetchone()  # 读取查询结果

    print(f"PostgreSQL connection successful: {result}")  # 在 Airflow task log 里输出连接成功信息


def extract_raw_data():
    raw_dataframes = extract_all()  # 调用 ingestion.extract，读取所有 raw CSV

    for table_name, dataframe in raw_dataframes.items():
        print(f"Extracted {len(dataframe)} rows from {table_name}")  # 输出每张表的行数，方便 debug 数据源问题


def validate_raw_data():
    raw_dataframes = extract_all()  # validation task 独立读取原始 CSV，避免依赖前一个 task 传 DataFrame
    validate_all(raw_dataframes)  # 调用 ingestion.validate，检查 schema、主键、日期、业务规则和外键关系

    print("Raw data validation completed successfully.")  # 如果这行出现，说明数据质量检查已通过


def transform_raw_data():
    raw_dataframes = extract_all()  # transform task 独立读取原始 CSV
    validate_all(raw_dataframes)  # 先验证再转换，避免脏数据进入转换逻辑
    transformed_dataframes = transform_all(raw_dataframes)  # 调用 ingestion.transform，清理字段和转换类型

    for table_name, dataframe in transformed_dataframes.items():
        print(f"Transformed {table_name}: {dict(dataframe.dtypes)}")  # 输出字段类型，方便定位类型转换问题


def load_transformed_data_to_postgres():
    raw_dataframes = extract_all()  # load task 独立读取原始 CSV，保证 task 可以单独重跑
    validate_all(raw_dataframes)  # 加载前再次验证，避免跳过上游 task 时加载坏数据
    transformed_dataframes = transform_all(raw_dataframes)  # 加载前生成最终要写入数据库的数据
    load_all(transformed_dataframes)  # 调用 ingestion.load_to_postgres，把数据写入 PostgreSQL

    print("Transformed data loaded into PostgreSQL successfully.")  # 在 Airflow log 中标记加载成功


default_args = {
    "owner": "korusafe",  # DAG owner，方便在 Airflow UI 中识别责任方
    "depends_on_past": False,  # 本次运行不依赖上一次运行结果
    "retries": 1,  # task 失败后自动重试 1 次
    "retry_delay": timedelta(minutes=2),  # 失败后等待 2 分钟再重试
}  # 所有 task 的默认参数


with DAG(
    dag_id="korusafe_pipeline",  # Airflow UI 中显示的 DAG 名称
    description="Load and validate KoruSafe workplace safety data into PostgreSQL.",  # DAG 描述
    default_args=default_args,  # 使用上面定义的默认参数
    start_date=datetime(2026, 1, 1),  # DAG 的逻辑开始日期
    schedule=None,  # 手动触发，不自动定时运行
    catchup=False,  # 不补跑历史日期
    tags=["korusafe", "data-engineering", "postgres"],  # Airflow UI 中的标签
) as dag:
    check_database = PythonOperator(
        task_id="check_postgres_connection",  # 第一步：检查 PostgreSQL 是否可连接
        python_callable=check_postgres_connection,  # 这个 task 执行的 Python 函数
    )  # 数据库连不上时，pipeline 不应该继续跑

    extract = PythonOperator(
        task_id="extract_raw_data",  # 第二步：读取 raw CSV
        python_callable=extract_raw_data,  # 调用 extract task 函数
    )  # 如果 CSV 路径或文件有问题，会在这里失败

    validate = PythonOperator(
        task_id="validate_raw_data",  # 第三步：验证原始数据质量
        python_callable=validate_raw_data,  # 调用 validate task 函数
    )  # 如果 schema、主键、日期或外键有问题，会在这里失败

    transform = PythonOperator(
        task_id="transform_raw_data",  # 第四步：转换和清理数据
        python_callable=transform_raw_data,  # 调用 transform task 函数
    )  # 如果类型转换失败，会在这里失败

    load = PythonOperator(
        task_id="load_transformed_data_to_postgres",  # 第五步：加载到 PostgreSQL
        python_callable=load_transformed_data_to_postgres,  # 调用 load task 函数
    )  # 如果表不存在、连接失败或写入失败，会在这里失败

    check_database >> extract >> validate >> transform >> load  # 定义 DAG task 执行顺序
