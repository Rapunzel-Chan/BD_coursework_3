import requests


def get_company_vacancies(employer_id):
    """Функция запроса информации о компаниях из API hh.ru"""
    url = f'https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100'
    response = requests.get(url)
    return response.json()['items']


def get_company_info(employer_id):
    """Функция для заполнения данных о вакансиях у компаний в базе данных"""
    url = f'https://api.hh.ru/employers/{employer_id}'
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    print(get_company_vacancies(1356767))
    print(get_company_info(1356767))
