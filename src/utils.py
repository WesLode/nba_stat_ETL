import functools
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

def get_data_sample(file, sample_size=10):
    with open(file, 'r',encoding='utf-8') as f1:
        temp = json.load(f1)
    result = []
    sample_count = 0
    for table in temp:
        for j in temp[table]:
            if sample_count >=sample_size:
                break
            sample_count +=1
            result+=[j]
        export_to_file(f'{table}',{
            table: result,
            },
            output_dir= f'output\\data\\sample'
        )


def retry(max_retries=3, delay=1, exceptions=(Exception,)):
    """Decorator to retry a function call."""
    def decorator_retry(func):
        @functools.wraps(func) # Preserves original function metadata
        def wrapper_retry(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    print(f"Decorator: Attempt {attempt + 1}/{max_retries} for {func.__name__}")
                    return func(*args, **kwargs) # Call the decorated function
                except exceptions as e: # Catch only specified exceptions
                    print(f"Decorator: Attempt {attempt + 1} failed: {e}")
                    last_exception = e
                    if attempt == max_retries - 1:
                        print("Decorator: All retries failed.")
                        raise # Re-raise the last caught exception
                    else:
                        print(f"Decorator: Waiting {delay}s...")
                        time.sleep(delay)
            # This should not be reached if exceptions are raised correctly
            # but ensures we raise if loop finishes unexpectedly
            raise RuntimeError("Retry loop exited without success or exception") from last_exception
        return wrapper_retry
    return decorator_retry

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