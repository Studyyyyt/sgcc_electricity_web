import yaml
import os
import platform
import json

VERSION = 'test version'
if os.path.exists('VERSION'):
    with open("VERSION", "r") as file:
        VERSION = file.readline()

data = {}
run_type = ''
if os.path.exists('/data/options.json'):
    # addons
    with open("/data/options.json", "r") as file:
        data = json.load(file)
    run_type = 'add-ones'
elif os.path.exists('config.yaml'):
    # docker
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)
    run_type = 'docker'
    

DEBUG = False
if platform.system() == 'Windows':
    run_type = 'windows'
    DEBUG = True

electricity = {
    'phone_number': data['electricity']['phone_number']
    ,'password': data['electricity']['password']
    ,'deiver_impltcity_wait_time': int(data['electricity'].get('deiver_impltcity_wait_time', '60'))
    ,'retry_times_limit': int(data['electricity'].get('retry_times_limit', '5'))
    ,'login_expected_time': int(data['electricity'].get('login_expected_time', '60'))
    ,'retry_wait_time_offset_unit': int(data['electricity'].get('retry_wait_time_offset_unit', '10'))
    ,'data_retention_days': int(data['electricity'].get('data_retention_days', '7'))
    ,'ignore_user_id': data['electricity'].get('ignore_user_id', [])
}

db = data['db']

logger = {
    'level': data['logger'].get('level', 'INFO').upper()
}

data_path = "/config" if run_type == 'add-ones' else data['data']['path']
os.makedirs(data_path, exist_ok=True) 

web = {
    'port': 8080 if run_type == 'add-ones' else int(data['web'].get('port', '8080'))
}

if __name__ == '__main__':
    print('---VERSION---')
    print(VERSION)
    print('---run_type---')
    print(run_type)
    print('---electricity---')
    print(electricity)
    print('---db---')
    print(db)
    print('---logger---')
    print(logger)
    print('---data_path---')
    print(data_path)
    print('---web---')
    print(web)