from configparser import ConfigParser
import os

EMPLOYERS = [2324020, 1035394, 4934, 25022, 2136954, 8884, 78638, 3388, 1057, 906557]
ROOT_DIR = os.path.dirname(__file__)
DATABASE_DIR = os.path.join(ROOT_DIR, 'database.ini')

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(DATABASE_DIR)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file.')

    return db
