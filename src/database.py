import psycopg2
from typing import Dict, Any
from config import config


def create_database() -> None:
    params = config()
    db_name = params['database']

    if not db_name.replace('_', '').isalnum():
        raise ValueError("Invalid database name!")
    conn = psycopg2.connect(
        dbname="postgres",
        user=params['user'],
        password=params['password'],
        host=params.get('host', 'localhost'),
        port=params.get('port', 5432)
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS %s" % db_name)
    cur.execute("CREATE DATABASE %s" % db_name)

    cur.close()
    conn.close()


def create_tables() -> None:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            company_id SERIAL PRIMARY KEY,
            hh_id INTEGER UNIQUE,
            name VARCHAR(255) NOT NULL,
            url TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            salary_from INTEGER,
            salary_to INTEGER,
            url TEXT,
            company_id INTEGER REFERENCES companies(company_id)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_company(cur, company_data: Dict[str, Any]) -> None:
    cur.execute("""
        INSERT INTO companies (hh_id, name, url)
        VALUES (%s, %s, %s)
        ON CONFLICT (hh_id) DO NOTHING
    """, (company_data['id'], company_data['name'], company_data['alternate_url']))


def insert_vacancy(cur, vacancy: Dict[str, Any], company_id: int) -> None:
    salary = vacancy.get('salary') or {}
    cur.execute("""
        INSERT INTO vacancies (title, salary_from, salary_to, url, company_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        vacancy['name'],
        salary.get('from'),
        salary.get('to'),
        vacancy['alternate_url'],
        company_id
    ))


if __name__ == "__main__":

    create_database()
    create_tables()
    company_data = {
        'id': 123456,
        'name': 'ООО Пример',
        'alternate_url': 'https://example.com'
    }


    vacancy_data = {
        'name': 'Разработчик Python',
        'alternate_url': 'https://example.com/vacancy/1',
        'salary': {
            'from': 80000,
            'to': 120000
        }
    }
    params = config()
    try:
        conn = psycopg2.connect(**params)
        with conn:
            with conn.cursor() as cur:

                insert_company(cur, company_data)

                cur.execute("SELECT company_id FROM companies WHERE hh_id = %s", (company_data['id'],))
                company_id = cur.fetchone()[0]

                insert_vacancy(cur, vacancy_data, company_id)
        print("Данные успешно вставлены.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
