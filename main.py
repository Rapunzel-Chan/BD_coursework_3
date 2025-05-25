from src.database import create_database, create_tables, insert_company, insert_vacancy
from src.hh_api import get_company_info, get_company_vacancies
from src.db_manager import DBManager
from config import config, EMPLOYERS
import psycopg2


# EMPLOYERS = [1356767, 5331842, 2104558, 1489461, 2180, 1457962, 99966, 11932968, 557095, 1272486]

def format_salary(salary_from, salary_to):
    """Функция для обработки разных форматов зарплат вакансий в базе данных"""
    if salary_from and salary_to:
        return f"{salary_from}–{salary_to} ₽"
    elif salary_from:
        return f"от {salary_from} ₽"
    elif salary_to:
        return f"до {salary_to} ₽"
    else:
        return "Зарплата не указана"

def main():
    """Функция для автоматического создания базы данных и взаимодействия с пользователем"""
    print("Создание базы данных...")
    create_database()
    create_tables()

    params = config()

    try:
        conn = psycopg2.connect(**params)
        with conn:
            with conn.cursor() as cur:
                for employer_id in EMPLOYERS:
                    company = get_company_info(employer_id)
                    if company and 'id' in company:
                        # Вставляем компанию, если она еще не существует
                        insert_company(cur, company)

                        # Получаем company_id из таблицы companies по hh_id
                        cur.execute("SELECT company_id FROM companies WHERE hh_id = %s", (company['id'],))
                        result = cur.fetchone()
                        if result:
                            company_id = result[0]
                        else:
                            print(f"Компания с hh_id {company['id']} не найдена в таблице companies.")
                            continue

                        # Получаем вакансии и вставляем их
                        vacancies = get_company_vacancies(employer_id)
                        for vacancy in vacancies:
                            insert_vacancy(cur, vacancy, company_id)

        manager = DBManager(params)

        print("\n Компании и количество вакансий:")
        for name, count in manager.get_companies_and_vacancies_count():
            print(f"{name}: {count} вакансий")

        print("\n Все вакансии:")
        for row in manager.get_all_vacancies():
            salary_str = format_salary(row[2], row[3])
            print(f"{row[0]} | {row[1]} | {salary_str} | {row[4]}")

        avg = manager.get_avg_salary()
        if avg:
            print(f"\n Средняя зарплата: {avg:.2f} ₽")
        else:
            print("\nНет данных для средней зарплаты")

        print("\n Вакансии с зарплатой выше средней:")
        for title, s_from, s_to in manager.get_vacancies_with_higher_salary():
            salary_str = format_salary(s_from, s_to)
            print(f"{title} | {salary_str}")

        keyword = input("\nВведите ключевое слово: ")
        print(f"\n Вакансии по ключевому слову '{keyword}':")
        for title, url in manager.get_vacancies_with_keyword(keyword.lower()):
            print(f"{title}: {url}")

        manager.close_connection()

    except Exception as e:
        print("Произошла ошибка: " + str(e))

if __name__ == "__main__":
    main()
