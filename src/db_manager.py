import psycopg2
from typing import List, Tuple, Optional

class DBManager:
    """Класс для взаимодействия с вакансиями в базе данных"""
    def __init__(self, db_params):
        self.conn = psycopg2.connect(**db_params)
        self.conn.autocommit = True

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Метод для заполнения данных о компаниях и вакансиях в базе данных"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(v.vacancy_id)
                FROM companies c
                LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.name
            """)
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Метод для заполнения данных обо всех вакансиях в базе данных"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
            """)
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """Метод для выборки данных о среднем значении по выбранным вакансиям в базе данных"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, Optional[int], Optional[int]]]:
        """Метод для выборки данных о вакансиях с зарплатой выше среднего показателя в базе данных"""
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            return []

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT title, salary_from, salary_to
                FROM vacancies
                WHERE ((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0) > %s
            """, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str]]:
        """Метод для выборки вакансий по ключевому слову в базе данных"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT title, url
                FROM vacancies
                WHERE title ILIKE %s
            """, (f'%{keyword}%',))
            return cur.fetchall()

    def close_connection(self):
        self.conn.close()
