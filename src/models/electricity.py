import logging
import os
import sqlite3
from datetime import datetime, timedelta
import config

class Electricity:
    def __init__(self, db_name):
        self.db_name = db_name
        self.is_db_new_create = False

        db_path = config.data_path + os.path.sep + self.db_name
        if not os.path.exists(db_path):
            logging.info(f"Database of {db_path} not exists, will created!")
            self.is_db_new_create = True
            self.connect = sqlite3.connect(db_path, check_same_thread=False)
            self._create_tables()
        else:
            self.connect = sqlite3.connect(db_path, check_same_thread=False)

    def _create_tables(self):
        logging.info(f"Start create tables...")
        cursor = self.connect.cursor()
        sql = """
           create table daily (
               user_code text not null
               ,date date not null
               ,usage real not null
               ,create_time date not null default current_timestamp
               ,update_time date not null default current_timestamp
               ,primary key(user_code, date)
           );
        """
        cursor.execute(sql)

        sql = """
           create table balance (
               user_code text primary key not null
               ,balance real not null
               ,create_time date not null default current_timestamp
               ,update_time date not null default current_timestamp
           );
        """
        cursor.execute(sql)

        sql = """
           create table month (
               user_code text not null
               ,date date not null
               ,usage real not null
               ,charge real not null
               ,create_time date not null default current_timestamp
               ,update_time date not null default current_timestamp
               ,primary key(user_code, date)
           );
        """
        cursor.execute(sql)

        sql = """
           create table year (
               user_code text not null
               ,date date not null
               ,usage real not null
               ,charge real not null
               ,create_time date not null default current_timestamp
               ,update_time date not null default current_timestamp
               ,primary key(user_code, date)
           );
        """
        cursor.execute(sql)
    
        cursor.close()
        logging.info(f"End create tables.")
    
    def close(self):
        self.connect.close()
         
    def insert_all_daily_info(self, user_code: str, data_list: list):
        cursor = self.connect.cursor()
        for data in data_list:
            sql = f"""
                insert or replace into daily(user_code, date, usage, update_time)
                values
                ('{user_code}', strftime('%Y-%m-%d','{data['date']}'), {data['usage']}, current_timestamp)
                on conflict(user_code, date) do update set
                usage = excluded.usage
                ,update_time = excluded.update_time
            """
            cursor.execute(sql)
        self.connect.commit()
        cursor.close()

    def insert_daily_info(self, user_code: str, date: str , usage: float):
        cursor = self.connect.cursor()
        sql = f"""
            insert or replace into daily(user_code, date, usage, update_time)
            values
            ('{user_code}', strftime('%Y-%m-%d','{date}'), {usage}, current_timestamp)
            on conflict(user_code, date) do update set
            usage = excluded.usage
            ,update_time = excluded.update_time
        """
        cursor.execute(sql)
        self.connect.commit()
        cursor.close()

    def insert_balance_info(self, user_code: str, balance: float):
        cursor = self.connect.cursor()
        sql = f"""
            insert or replace into balance(user_code, balance, update_time)
            values
            ('{user_code}', {balance}, current_timestamp)
            on conflict(user_code) do update set
            balance = excluded.balance
            ,update_time = excluded.update_time
        """
        cursor.execute(sql)
        self.connect.commit()
        cursor.close()

    def insert_month_info(self, user_code: str, date: str, usage: float, charge: float):
        cursor = self.connect.cursor()
        sql = f"""
            insert or replace into month(user_code, date, usage, charge, update_time)
            values
            ('{user_code}', strftime('%Y-%m-%d','{date}'), {usage}, {charge}, current_timestamp)
            on conflict(user_code, date) do update set
            usage = excluded.usage
            ,charge = excluded.charge
            ,update_time = excluded.update_time
        """
        cursor.execute(sql)
        self.connect.commit()
        cursor.close()
    
    def insert_year_info(self, user_code: str, date: str, usage: float, charge: float):
        cursor = self.connect.cursor()
        sql = f"""
            insert or replace into year(user_code, date, usage, charge, update_time)
            values
            ('{user_code}', strftime('%Y-%m-%d','{date}'), {usage}, {charge}, current_timestamp)
            on conflict(user_code, date) do update set
            usage = excluded.usage
            ,charge = excluded.charge
            ,update_time = excluded.update_time
        """
        cursor.execute(sql)
        self.connect.commit()
        cursor.close()

    def __exe_select(self, sql: str):
        cursor = self.connect.cursor()
        result = cursor.execute(sql)
        return result
    
    def get_user_list(self):
        sql = """
            select
                user_code
            from balance
        """
        user_code_list = self.__exe_select(sql)
        result = []
        for item in user_code_list:
            result.append(item[0])
        return result
    
    def get_user_balance(self, userId: str):
        sql = f"""
            select
                balance
                ,update_time
            from balance
            where user_code = {userId}
        """
        balance = self.__exe_select(sql)
        result = {}
        for item in balance:
            result = {
                'balance': item[0]
                ,'updateTime': (datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S") + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            }

        return result
    
    def get_user_dailys(self, userId: str):
        sql = f"""
            select
                date
                ,usage
            from daily
            where user_code = {userId}
            order by date desc
            limit 7
        """
        year = self.__exe_select(sql)
        result = []
        for item in year:
            result.append({
                'date': item[0]
                ,'usage': item[1]
            })

        return result
    
    def get_user_latest_month(self, userId: str):
        sql = f"""
            select 
                date
                ,usage
                ,charge
            from month
            where user_code = {userId} 
            order by date desc 
            limit 1
        """
        month = self.__exe_select(sql)
        result = {}
        for item in month:
            result = {
                'date': item[0]
                ,'usage': item[1]
                ,'charge': item[2]
            }
        
        return result
    
    def get_user_this_year(self, userId: str):
        sql = f"""
            select
                date
                ,usage
                ,charge
            from year
            where user_code = {userId}
             and date = '{datetime.now().strftime('%Y-01-01')}'
        """
        year = self.__exe_select(sql)
        result = {}
        for item in year:
            result = {
                'date': item[0]
                ,'usage': item[1]
                ,'charge': item[2]
            }
        
        return result

if __name__ == "__main__":
    saver = DataSaveer("test.db")
    daily_list = [
        {'date': '2024-12-06', 'usage': 1.0}
        ,{'date': '2024-12-07', 'usage': 2.0}
        ,{'date': '2024-12-08', 'usage': 3.0}
        ,{'date': '2024-12-09', 'usage': 4.0}
        ,{'date': '2024-12-10', 'usage': 5.0}
    ]
    saver.insert_all_daily_info('789', daily_list)
    saver.insert_daily_info("123", "2024-12-12", 5.6)
    saver.insert_month_info("123", "2024-12-13", 4.7, 10.4)
    saver.insert_year_info("123", "2024-12-13", 8.9, 19.0)
    saver.insert_balance_info("123", 1000.6)
    saver.close()