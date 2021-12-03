import os
import pickle as pk
import datetime
import easyquotation as eq
import numpy as np
import pandas as pd
import tushare as ts
import uiautomator2 as u2
from automator import StockProcess
from apscheduler.schedulers.blocking import BlockingScheduler


class SmallShort(object):

    def __init__(self, code_list, init=False):
        self.code_list = code_list
        if init:
            self.stock_dict = {}
            self.init_dict()
            self.record = pd.DataFrame(
                columns=['时间', '股票名称/代码', '今日盈亏', '成本/现价', '持仓'])
            self.record.set_index(['时间', '股票名称/代码'], inplace=True)
            self.record.to_csv('record.csv', encoding='utf-8')
        else:
            with open('stock_dict.pk', 'rb') as sd:
                self.stock_dict = pk.load(sd)
            print(self.stock_dict.keys())
            self.record = pd.read_csv('record.csv')
            self.record.set_index(['时间', '股票名称/代码'], inplace=True)
        # self.record = pd.DataFrame(columns = ['股票名称/代码', '今日盈亏', '成本/现价','持仓'])

        self.now_time = datetime.datetime.now().date()
        self.sp = StockProcess()

    def init_dict(self):
        for each_code in self.code_list[:]:
            self.stock_dict[each_code] = {}
            self.stock_dict[each_code]['is_have'] = 0
        with open('stock_dict.pk', 'wb') as sd:
            pk.dump(self.stock_dict, sd)

    def before_trading(self):
        pro = ts.pro_api(token='420640ebd106e2cb753a775af0645ee306a8d871571b0565889f74d6')

        for each_code in self.code_list[:]:
            ts_code = each_code.replace('XSHG', 'SH')
            ts_code = ts_code.replace('XSHE', 'SZ')

            df = pro.daily(ts_code=ts_code, start_date='20210101')
            last4 = df.loc[:3, 'close'].values
            last9 = df.loc[:8, 'close'].values
            ma5 = df.loc[:4, 'close'].mean()
            ma10 = df.loc[:9, 'close'].mean()

            if ma5 > ma10:
                last_status = 1
            else:
                last_status = -1
            self.stock_dict[each_code]['last_status'] = last_status

            self.stock_dict[each_code]['last4'] = last4
            self.stock_dict[each_code]['last9'] = last9
            self.stock_dict[each_code]['last_ma5'] = ma5
            self.stock_dict[each_code]['last_ma10'] = ma10
        print("数据初始化成功!")

    def on_trading(self, d):
        quotation = eq.use('sina')
        print(datetime.datetime.now(),
              '-----------------------------------------------------')
        for each_code in self.stock_dict.keys():
            eq_code = each_code.replace('.XSHG', '')
            eq_code = eq_code.replace('.XSHE', '')

            current_data = quotation.real(eq_code)
            now_price = current_data[eq_code]['now']
            name = current_data[eq_code]['name']
            print(each_code, name)

            last4 = self.stock_dict[each_code]['last4']
            ma5 = np.append(last4, now_price).mean()

            last9 = self.stock_dict[each_code]['last9']
            ma10 = np.append(last9, now_price).mean()

            last_status = self.stock_dict[each_code]['last_status']
            if ma5 > ma10:
                status = 1
            else:
                status = -1

            if last_status == status:
                if self.stock_dict[each_code]['is_have']:
                    hold_price = self.stock_dict[each_code]['hold_price']
                    return_rate = (now_price - hold_price) / hold_price
                    if return_rate > 0.1:
                        self.stock_dict[each_code]['is_have'] = 0
                        amount = self.stock_dict[each_code]['amount']
                        self.sp.sell(
                            d, eq_code, price=now_price, amount=amount)
                        print(
                            f'卖出股票: {each_code}, 卖出价格: {now_price}, '
                            f'收益率: {return_rate}, 数量: {amount}')
                        earn_loss = (now_price - hold_price) * amount
                        self.record.loc[(self.now_time, f'{name}:{each_code}'), :] = earn_loss, f'{hold_price}\{now_price}', f'0\{amount}'
                else:
                    print(f'没有股票 {name}:{each_code}, 状态:0')
            elif status == 1:
                if not self.stock_dict[each_code]['is_have']:
                    amount = ((10000 // now_price) // 100) * 100
                    self.stock_dict[each_code]['is_have'] = 1
                    self.stock_dict[each_code]['hold_price'] = now_price
                    self.stock_dict[each_code]['amount'] = amount
                    self.sp.buy(d, eq_code, price=now_price, amount=amount)
                    print(f'买入股票: {each_code}, 买入价格: {now_price}, 数量: {amount}')
                    self.record.loc[(self.now_time, f'{name}:{each_code}'), :] = 0, now_price, amount
                    # self.stock_dict[each_code]['last_status'] = status
                else:
                    print(f'已有股票 {name}:{each_code}, 状态:1')
            elif status == -1:
                if self.stock_dict[each_code]['is_have']:
                    self.stock_dict[each_code]['is_have'] = 0
                    hold_price = self.stock_dict[each_code]['hold_price']
                    return_rate = (now_price - hold_price) / hold_price
                    amount = self.stock_dict[each_code]['amount']
                    self.sp.sell(d, eq_code, price=now_price, amount=amount)
                    print(
                        f'卖出股票: {each_code}, 卖出价格: {now_price}, '
                        f'收益率: {return_rate}, 数量: {amount}')
                    earn_loss = (now_price - hold_price) * amount
                    self.record.loc[(self.now_time, f'{name}:{each_code}'), :] = earn_loss, f'{hold_price}\{now_price}', f'0\{amount}'
                else:
                    print(f'没有股票 {name}:{each_code}, 状态: -1')
        print('\n\n\n')

    def after_trading(self):
        quotation = eq.use('sina')
        for each_code in self.stock_dict.keys():
            eq_code = each_code.replace('.XSHG', '')
            eq_code = eq_code.replace('.XSHE', '')

            current_data = quotation.real(eq_code)
            now_price = current_data[eq_code]['now']
            name = current_data[eq_code]['name']

            if self.stock_dict[each_code]['is_have']:
                hold_price = self.stock_dict[each_code]['hold_price']
                amount = self.stock_dict[each_code]['amount']
                earn_loss = (now_price - hold_price) * amount
                self.record.loc[(self.now_time, f'{name}:{each_code}'), :] = earn_loss, f'{hold_price}\{now_price}', f'0\{amount}'

            self.record.to_csv('record.csv')
            with open('stock_dict.pk', 'wb') as sd:
                pk.dump(self.stock_dict, sd)
        print("数据存储成功!")


if __name__ == '__main__':
    start = int(input('ATX启动状态【0/1】--0为未启动，1为已启动:'))
    if not start:
        init = 'python -m uiautomator2 init'
        os.system(init)
    wifi_input = input('输入 wifi ip地址: ')
    init = int(input("是否初始化【0/1】--0为否，1为是: "))
    d = u2.connect(wifi_input)

    now_time = datetime.datetime.now()
    start_time = datetime.datetime(
        now_time.year, now_time.month, now_time.day, 9, 45, 1)
    end_time = datetime.datetime(
        now_time.year, now_time.month, now_time.day, 15, 1, 1)

    scheduler = BlockingScheduler()

    code_list = ['300589.XSHE', '300581.XSHE', '002164.XSHE', '000633.XSHE',
                          '603063.XSHG', '600438.XSHG', '002202.XSHE', '300343.XSHE',
                          '002348.XSHE', '300712.XSHE']

    ss = SmallShort(init=init, code_list=code_list)
    # ss.before_trading()
    # ss.on_trading(d)
    # ss.after_trading()

    scheduler.add_job(ss.before_trading, 'date', run_date=now_time)
    scheduler.add_job(ss.on_trading, args=(d,), trigger='interval',
                      minutes=1, start_date=start_time, end_date=end_time)
    scheduler.add_job(ss.after_trading, 'date', run_date=end_time)

    scheduler.start()
