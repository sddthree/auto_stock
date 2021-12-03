import tushare as ts
from tqdm import tqdm
import pandas as pd
import pymysql
import sys
import time
from sqlalchemy import create_engine

pro = ts.pro_api(token='？？？')

def get_all_stock_info():
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data.to_csv('./data/all_stocks.csv', encoding='utf-8')
    return data

def get_stock_daily_detail(ts_code, start_date='20180701', end_date='20211121'):
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return df

def read_mysql_and_insert(df, name, read=False):
    # pymysql for df read_sql
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='？？？', db='stock', charset='utf8')
    except pymysql.err.OperationalError as e:
        print('Error is ' + str(e))
        sys.exit()

    # sqlalchemy for df to_sql
    try:
        engine = create_engine('mysql+pymysql://root:？？？@127.0.0.1:3306/stock')
    except sqlalchemy.exc.OperationalError as e:
        print('Error is ' + str(e))
        sys.exit()
    except sqlalchemy.exc.InternalError as e:
        print('Error is ' + str(e))
        sys.exit()

    if read:
        try:
            # pymysql 读取数据库，返回df类型数据
            sql = f"select * from {name}"
            df = pd.read_sql(sql, con=conn)
        except pymysql.err.ProgrammingError as e:
            print('Error is ' + str(e))
            sys.exit()
        return df

    # sqlalchemy 存取df类型数据到数据库
    df.to_sql(name=name[:-3],con=engine,if_exists='append',index=False)
    conn.close()
    # print('ok')

if __name__ == '__main__':
    data = get_all_stock_info()
    read_mysql_and_insert(data, 'all_stocks')
    code_list = data.dropna().ts_code
    for each_code in tqdm(code_list):
        df = get_stock_daily_detail(each_code)
        read_mysql_and_insert(df, each_code)
        time.sleep(0.3)
