import requests

def get_company_vacancies(employer_id):
    url = f'https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100'
    response = requests.get(url)
    return response.json()['items']


def get_company_info(employer_id):
    url = f'https://api.hh.ru/employers/{employer_id}'
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    print(get_company_vacancies(1356767))
    print(get_company_info(1356767))
