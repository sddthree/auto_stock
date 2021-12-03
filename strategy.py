import pymysql
import pandas as pd
import numpy as np
import tushare as ts
from tqdm import tqdm
from sqlalchemy import create_engine
from getdata import read_mysql_and_insert
from datetime import date,timedelta,datetime

pro = ts.pro_api(token='420640ebd106e2cb753a775af0645ee306a8d871571b0565889f74d6')

def strategy():
    """
    auto strategy
    """
    # 获取处理好后的股票信息
    all_stock_info = deal_all_stock_info()
    # 最终结果记录
    result = pd.DataFrame(index=all_stock_info.ts_code)
    # 对每支股票进行分析
    for idx, row in tqdm(all_stock_info.iterrows(), total=all_stock_info.shape[0]):
        # 获取股票名字
        code_name = row['name']
        code = row['ts_code']
        if code[0] not in ['0','3','6']:
            continue
        one_code = '`'+code[:-3]+'`'
        # 获取每支股票前180个交易日
        one_stock_detail = read_mysql_and_insert(df=None, name=one_code, read=True)
        one_stock_detail['trade_date'] = pd.to_datetime(one_stock_detail['trade_date'])
        one_stock_detail.set_index('trade_date', inplace=True)
        # 计算最大波动率
        volatility_180 = (one_stock_detail.close.max() - one_stock_detail.close.min()) / one_stock_detail.close.max()
        if volatility_180 > 0.2:
            init_stock_data(one_stock_detail)
            result.loc[code, 'code_name'] = code_name
            if one_stock_detail.close.idxmax() > one_stock_detail.close.idxmin(): # ?
                trend = '上涨趋势'
                result.loc[code, 'trend'] = trend
            else:
                trend = '下跌趋势'
                result.loc[code, 'trend'] = trend
            result.loc[code, 'MA5_10_return'] = calculate_return(one_stock_detail, ma='MA5_10')
            result.loc[code, 'MA5_20_return'] = calculate_return(one_stock_detail, ma='MA5_20')
            result.loc[code, 'MA5_30_return'] = calculate_return(one_stock_detail, ma='MA5_30')
    return result


def init_stock_data(stock_data):
    # create ma
    stock_data['MA5'] = stock_data['close'].rolling(window=5).mean()
    stock_data['MA10'] = stock_data['close'].rolling(window=10).mean()
    stock_data['MA20'] = stock_data['close'].rolling(window=20).mean()
    stock_data['MA30'] = stock_data['close'].rolling(window=30).mean()
    stock_data['MA60'] = stock_data['close'].rolling(window=60).mean()
    
    # return_rate
    # stock_data['return_rate'] = 1 + stock_data['pct_chg']/100
    stock_data['return_rate'] = stock_data['close'].rolling(window=2).apply(lambda x: 1 + (x[1]-x[0])/x[0], raw=False)
    
    #fillna
    stock_data.fillna(0, inplace=True)

    # return
    
    # 5_10
    stock_data['MA5_10'] = np.sign(stock_data.MA5 - stock_data.MA10)
    stock_data['MA5_10'] = stock_data['MA5_10'].rolling(window=2).apply(lambda x: deal_with_ma(x), raw=False)

    # 5_20
    stock_data['MA5_20'] = np.sign(stock_data.MA5 - stock_data.MA20)
    stock_data['MA5_20'] = stock_data['MA5_20'].rolling(window=2).apply(lambda x: deal_with_ma(x), raw=False)

    # 5_30
    stock_data['MA5_30'] = np.sign(stock_data.MA5 - stock_data.MA30)
    stock_data['MA5_30'] = stock_data['MA5_30'].rolling(window=2).apply(lambda x: deal_with_ma(x), raw=False)
    
    # fillna
    stock_data.fillna(0, inplace=True)

def calculate_return(stock_data, init_money=1, ma='MA5_10'):
    # MA5_10 从1开始， 而后每个 [1,-1]区间进行计算
    if stock_data[stock_data[ma]!=0].empty:
        return init_money
    if stock_data[stock_data[ma]!=0].iloc[0][ma] == -1:
        stock_data.drop(index=stock_data[stock_data[ma]!=0].index[0], inplace=True)
    a = np.where(stock_data[ma]==1)[0]
    b = np.where(stock_data[ma]==-1)[0]
    effective_area_list = list(zip(a,b))
    
    for each_period in effective_area_list:
        start_ix, end_ix = each_period
        return_sell_threshold = 1
        if stock_data.iloc[start_ix].close > stock_data.iloc[start_ix].MA60:
            continue
        for each_ix in range(start_ix, end_ix+1):
            return_sell_threshold *= stock_data.iloc[each_ix].return_rate
            if return_sell_threshold >= 1.1:
                break
        init_money *= return_sell_threshold
    return init_money

def deal_with_ma(x):
    if (x[0] == x[1]) or (x[0] == 0) or (x[1] == 0):
        return 0
    else:
        if x[0] == 1:
            # 长线穿过短线: 如20日线穿过5日线
            return -1
        if x[0] == -1:
            # 短线穿过长线: 如5日线穿过20日线
            return 1

def deal_all_stock_info():
    # 1.获取所有股票信息
    all_stock_info = read_mysql_and_insert(df=None, name='all_sto', read=True)
    # 2.去掉其中科创板股票
    all_stock_info = all_stock_info[all_stock_info.ts_code.str.startswith('688')==False]
    # 3.去掉其中的ST股票
    all_stock_info = all_stock_info[all_stock_info.name.str.contains('ST')==False]
    # 4.去掉交易日不满180天的股票
    # 获取今天的日期，并转化成相应格式
    day=date.today()
    day=format(day.strftime('%Y%m%d'))
    # 利用query接口可直接获取一段时间的交易日，is_open指是否开盘，1即开盘，就是交易日
    data = pro.query('trade_cal', start_date='20210120',end_date=day,is_open='1')
    # 返回数据集中的cal_date字段即为交易日
    trade_days = list(data['cal_date'])
    #将交易日转换列表后，即可随意获取到最近交易日，上一个交易等
    last_day180 = trade_days[-180]
    all_stock_info = all_stock_info[all_stock_info['list_date']<last_day180]
    return all_stock_info


if __name__ == '__main__':
    result = strategy()
    result.to_excel('./result_all.xlsx')
    # # test one code
    # one_code = all_codes[1][:-3]
    # one_code = '`'+one_code+'`'
    # one_code_info = read_mysql_and_insert(df=None, name=one_code, read=True)
    # print(one_code_info.head())
