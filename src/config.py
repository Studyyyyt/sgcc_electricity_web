import yaml
import os

with open("config.yaml", "r") as file:
    data = yaml.safe_load(file)

VERSION = '0.0.1'

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

logger = data['logger']

data_path = data['data']['path']
os.makedirs(data_path, exist_ok=True) 

web = {
    'port': int(data['web'].get('port', '8080'))
}