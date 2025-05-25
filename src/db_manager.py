import psycopg2
from typing import List, Tuple, Optional

class DBManager:
    def __init__(self, db_params):
        self.conn = psycopg2.connect(**db_params)
        self.conn.autocommit = True

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, COUNT(v.vacancy_id)
                FROM companies c
                LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.name
            """)
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
            """)
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, Optional[int], Optional[int]]]:
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
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT title, url
                FROM vacancies
                WHERE title ILIKE %s
            """, (f'%{keyword}%',))
            return cur.fetchall()

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    db = DBManager()


    print("Компании и количество их вакансий:")
    companies = db.get_companies_and_vacancies_count()
    for name, count in companies:
        print(f"{name}: {count} вакансий")

    print("\nСписок всех вакансий:")
    vacancies = db.get_all_vacancies()
    for company, title, salary_from, salary_to, url in vacancies:
        print(f"{company} | {title} | от {salary_from or 'Не указана'} до {salary_to or 'Не указана'} | {url}")


    avg_salary = db.get_avg_salary()
    print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f}" if avg_salary else "Нет данных о зарплатах.")

    print("\nВакансии с зарплатой выше средней:")
    high_salary_vacancies = db.get_vacancies_with_higher_salary()
    for title, salary_from, salary_to in high_salary_vacancies:
        print(f"{title} | от {salary_from or 'Не указана'} до {salary_to or 'Не указана'}")

    keyword = 'Python'
    print(f"\nВакансии, содержащие ключевое слово '{keyword}':")
    keyword_vacancies = db.get_vacancies_with_keyword(keyword)
    for title, url in keyword_vacancies:
        print(f"{title} | {url}")

    db.close_connection()
