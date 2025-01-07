# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_apscheduler import APScheduler

import logging
from logging.config import dictConfig
from datetime import datetime, timedelta
import traceback
import config

import v1
from electricity.data_fetcher import DataFetcher
from models import electricity

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': "%(asctime)s  %(levelname)] %(message)s",
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }
    },
    'root': {
        'level': config.logger['level'],
        'handlers': ['console']
    }
})
fetcher = DataFetcher(config.electricity['phone_number'], config.electricity['password'])
app = Flask(__name__, static_folder='static')
scheduler = APScheduler()


@scheduler.task('cron', id='fetch_electricity_task', hour='7,19', misfire_grace_time=900)
def fetch_electricity_task():
    try:
        data = fetcher.fetch()
        
        for user_id in data.keys():
            user_data = data[user_id]

            try:
                if user_data['balance'] is not None:
                    electricity.insert_balance_info(user_id, user_data['balance'])

                if user_data['location'] is not None:
                    electricity.insert_location_info(user_id, user_data['location'])
                
                if user_data['last_daily'] is not None:
                    electricity.insert_daily_info(user_id, user_data['last_daily']['date'], user_data['last_daily']['usage'])
                
                if user_data['daily'] is not None:
                    electricity.insert_all_daily_info(user_id, user_data['daily'])

                if user_data['yearly'] is not None:
                    electricity.insert_year_info(user_id, str(datetime.now().year) + '-01-01', user_data['yearly']['usage'], user_data['yearly']['charge'])

                if user_data['month'] is not None:
                    for item in user_data['month']:
                        electricity.insert_month_info(user_id, item['date'][0:7] + '-01', item['usage'], item['charge'])

                logging.info(f"update {user_id} status successfully!")
            except Exception as e:
                logging.error(f"update {user_id} status failed, reason is {e}")
                traceback.print_exc()

        logging.info("state-refresh task run successfully!")
    except Exception as e:
        logging.error(f"state-refresh task failed, reason is {e}")
        traceback.print_exc()

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.register_blueprint(v1.bp, url_prefix='/v1')

    scheduler.init_app(app)

    if electricity.is_db_new_create:
        logging.info("db is new created, will init electricity data!!!")
        scheduler.add_job(func=fetch_electricity_task, trigger='date', next_run_time=(datetime.now() + timedelta(seconds=10)), id='init_electricity_task', misfire_grace_time=900)
    
    scheduler.start()

    from waitress import serve
    serve(app, host="0.0.0.0", port=config.web['port'])
    # app.run(debug=False)