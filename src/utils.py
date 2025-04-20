import json
from pathlib import Path
import logging
import os
import unicodedata
import time
from datetime import datetime
import pandas as pd
import requests

def clean_utf8(x):
    return unicodedata.normalize('NFD',x).encode('ascii', 'ignore')


def retry(func, retries=3):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print(e)
                time.sleep(30)
                attempts += 1

    return retry_wrapper

def export_to_file(f_name: str, sometext, output_dir="output/data", file_type ="json"):
    make_dir(output_dir)
    if file_type not in ["json","txt","html","md","yml","csv","sql"]:
        print("File type not supported.")
        return False
    if file_type == "json":
        sometext = json.dumps(sometext, indent=4, ensure_ascii= False)

    with open(f'{output_dir}/{f_name}.{file_type}', "w", encoding="utf-8") as outfile:
        outfile.write(sometext)

    return True


def add_to_list(my_list, new_item):
    if new_item not in my_list:
        my_list.append(new_item)
    return my_list

def make_dir(path):
    directory_path = Path(path)

    try:
        directory_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass

def get_nested(data, path):
    if path and data:
        element  = path[0]
        if element:
            # value = data.get(element)
            value = data[element]
            return value if len(path) == 1 else get_nested(value, path[1:])


class log_dir():
    def __init__(self):
        
        self.loc_dir = os.getcwd()
        self.detail_log_file = f'{self.loc_dir}\\log\\dir_manager_full.log'
        self.log_file = f'{self.loc_dir}\\log\\dir_manager_sum.log'

def get_time_stamp():
    return datetime.now().strftime(DATETIME_FORMAT)

def make_dir(path):
    directory_path = Path(path)

    try:
        directory_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass

def get_logger(name):
    loc_dir = os.getcwd()
    detail_log_file = f'{loc_dir}\\log\\dir_manager_full.log'
    log_file = f'{loc_dir}\\log\\dir_manager_sum.log'
    make_dir(f'{loc_dir}\\log')

    logger = logging.getLogger(name)
    # logger.setLevel('INFO')

    app_name = 'Directory Manager'
    formatter = logging.Formatter(f'<14>1 %(asctime)s.%(msecs)03dZ - {app_name} %(process)d - - %(levelname)s: (%(name)s) %(message)s',
                                      "%Y-%m-%dT%H:%M:%S")
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    
    formatter.converter = time.gmtime

    std_handler = logging.StreamHandler()
    std_handler.setLevel('INFO')
    std_handler.setFormatter(formatter)
    logger.addHandler(std_handler)

    file_handler = logging.FileHandler(detail_log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger



DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DATE_FORMATS = [
    '%Y-%m-%d',     # YYYY-MM-DD
    '%Y-%-m-%-d',   # YYYY-[M]M-[D]D
    '%m/%d/%Y',     # MM/DD/YYYY
    '%-m/%-d/%Y',   # [M]M/[D]D/YYYY
    '%Y/%m/%d',     # YYYY/MM/DD
    '%Y/%-m/%-d',   # YYYY/[M]M/[D]D
    '%Y%m%d',       # YYYYMMDD
    '%m-%d-%Y',     # MM-DD-YYYY
    '%-m-%-d-%Y',   # [M]M-[D]D-YYYY
    '%b %d %Y',     # MMM DD YYYY
    '%b %-d %Y',    # MMM [D]D YYYY
    '%d %b %Y',     # DD MMM YYYY
    '%-d %b %Y'     # [D]D MMM YYYY
]
DATETIME_FORMAT = '%Y%m%d-%H%M%S'



if __name__ == "__main__":
    log = get_logger('Test')
    log.debug('This is a debug message')
    log.info('This is an info message')
    log.warning('This is a warning message')
    log.error('This is an error message')
    log.critical('This is a critical message')