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
        'level': config.logger['level'].upper(),
        'handlers': ['console']
    }
})
fetcher = DataFetcher(config.electricity['phone_number'], config.electricity['password'])
app = Flask(__name__, static_folder='static')
scheduler = APScheduler()


@scheduler.task('cron', id='fetch_electricity_task', hour='7,19', misfire_grace_time=900)
def fetch_electricity_task():
    try:
        user_id_list, balance_list, last_daily_date_list, last_daily_usage_list, daily_usage_list, yearly_charge_list, yearly_usage_list, month_list, month_usage_list, month_charge_list = fetcher.fetch()
        
        for i in range(0, len(user_id_list)):
            try:
                if balance_list[i] is not None:
                    electricity.insert_balance_info(user_id_list[i], balance_list[i])
                
                if last_daily_usage_list[i] is not None:
                    electricity.insert_daily_info(user_id_list[i], last_daily_date_list[i], last_daily_usage_list[i])
                
                if daily_usage_list is not None:
                    electricity.insert_all_daily_info(user_id_list[i], daily_usage_list[i])

                if yearly_usage_list[i] is not None and yearly_charge_list[i] is not None:
                    electricity.insert_year_info(user_id_list[i], str(datetime.now().year) + '-01-01', yearly_usage_list[i], yearly_charge_list[i])

                if month_charge_list[i] is not None and month_usage_list[i] is not None:
                    electricity.insert_month_info(user_id_list[i], month_list[i][0:7] + '-01', month_usage_list[i], month_charge_list[i])

                logging.info(f"update {user_id_list[i]} status successfully!")
            except Exception as e:
                logging.error(f"update {user_id_list[i]} status failed, reason is {e}")
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