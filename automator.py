import os
import time
import datetime
import threading

import uiautomator2 as u2


class StockProcess(object):
    """
    股票操作
    """

    def __init__(self):
        self.price_dict = self._init_price_dict()
        self.amount_dict = self._init_amount_dict()
        self.stock_dict = self._init_stock_dict()

    def _init_price_dict(self):
        a = {}
        dx = 225
        dy = 117
        x0 = 112.5
        y0 = 1130
        k = 0
        for i in range(1, 4):
            col = y0 + (i-1)*dy
            for j in range(1, 4):
                k += 1
                row = x0 + (j-1)*dx
                a[k] = (row, col)

        a['.'] = (a[7][0], a[7][1]+dy)
        a[0] = (a[8][0], a[8][1]+dy)
        return a

    def _init_amount_dict(self):
        a = {}
        dx = 180
        dy = 117
        x0 = 180
        y0 = 1130
        k = 0
        for i in range(1, 4):
            col = y0 + (i-1)*dy
            for j in range(1, 4):
                k += 1
                row = x0 + (j-1)*dx
                a[k] = (row, col)

        a[0] = (a[8][0], a[8][1]+dy)
        return a

    def _init_stock_dict(self):
        a = {}
        dx = 250
        dy = 117
        x0 = 200
        y0 = 1130
        k = 0
        for i in range(1, 4):
            col = y0 + (i-1)*dy
            for j in range(1, 4):
                k += 1
                row = x0 + (j-1)*dx
                a[k] = (row, col)

        a[0] = (a[7][0], a[7][1]+dy)
        return a

    def _dclick(self, a, i):
        d.click(a[i][0],a[i][1])     

    def buy(self, d, code, price, amount):
        """
        购买股票操作
        :param self:
        :param d:
        :param code: 股票代码 str
        :param price: 输入购买价格 double
        :param amount: 输入购买数量 int
        :return:
        """
        #.........
        # 切换至交易界面
        d.xpath('//*[@content-desc="交易"]').click()
        time.sleep(1)
        # 点击买入
        d.xpath('//*[@resource-id="com.hexin.plat.android:id/menu_buy"]').click()
        time.sleep(1)
        # 点击输入股票
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/content_stock"]').click()
        time.sleep(1)
        # 输入股票代码/之后改为输入股票名字
        for i in code:
            self._dclick(self.stock_dict, int(i))
        time.sleep(1)
        # 选择股票
        d.xpath('//*[@resource-id="com.hexin.plat.android:id/recyclerView"]/android.widget.RelativeLayout[1]').click(timeout=1)
        time.sleep(1)
        # 点击价格
        d(resourceId="com.hexin.plat.android:id/stockprice").click(timeout=1)
        time.sleep(1)
        # 清空已有价格
        d(resourceId="com.hexin.plat.android:id/keyboard_key_clear").click()
        time.sleep(1)
        # 输入价格
        for i in str(price):
            if i == '.':
                self._dclick(self.price_dict, i)
            else:
                self._dclick(self.price_dict, int(i))
        # 点击数量
        d.xpath('//*[@resource-id="com.hexin.plat.android:id/stockvolume"]').click(timeout=1)
        time.sleep(1)
        # 输入数量
        for i in str(amount):
            self._dclick(self.amount_dict, int(i))
        # 点击买入
        time.sleep(1)
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/btn_transaction"]').click(timeout=1)
        time.sleep(1)
        # 买入确定提示
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/ok_btn"]').click(timeout=1)

        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/ok_btn"]').click(timeout=1)
        time.sleep(1)
        # 返回自选界面
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/title_bar_left_container"]').click(timeout=1)

        d.xpath('//*[@content-desc="自选"]').click(timeout=1)

        print("下单买入: ", code, " 价格: ", price, " 数量:", amount)

    def sell(self, d, code, price, amount):
        """
        卖出股票操作
        :param d:
        :param code: 股票代码 str
        :param price: 卖出价格 double
        :param amount: 卖出数量 int/str
        :return:
        """

        # 切换至交易界面
        d.xpath('//*[@content-desc="交易"]').click(timeout=1)
        # 点击卖出
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/menu_sale"]').click(timeout=1)
        # 点击输入股票
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/content_stock"]').click(timeout=1)
        # 输入股票代码
        for i in code:
            self._dclick(self.stock_dict, int(i))
        time.sleep(1)
        # 选择股票
        d.xpath('//*[@resource-id="com.hexin.plat.android:id/recyclerView"]/android.widget.RelativeLayout[1]').click(timeout=1)
        # 点击价格
        d(resourceId="com.hexin.plat.android:id/stockprice").click(timeout=1)
        # 清空已有价格
        d(resourceId="com.hexin.plat.android:id/keyboard_key_clear").click()
        # 输入价格
        for i in str(price):
            if i == '.':
                self._dclick(self.price_dict, i)
            else:
                self._dclick(self.price_dict, int(i))
        # 点击数量
        d.xpath('//*[@resource-id="com.hexin.plat.android:id/stockvolume"]').click(timeout=1)
        # 输入数量
        for i in str(amount):
            self._dclick(self.amount_dict, int(i))
        # 点击卖出
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/btn_transaction"]').click(timeout=1)
        # 卖出确定提示
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/ok_btn"]').click(timeout=1)

        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/ok_btn"]').click(timeout=1)

        # 返回自选界面
        d.xpath(
            '//*[@resource-id="com.hexin.plat.android:id/title_bar_left_container"]').click(timeout=1)

        d.xpath('//*[@content-desc="自选"]').click()

        print("下单卖出: ", code, " 价格: ", price, " 数量:", amount)

    def recall_k(self, k):
        """
        撤前k个单
        :param k: int
        :return:
        """
        d(description="交易").click()
        # 点击撤单
        d(resourceId="com.hexin.plat.android:id/menu_withdrawal").click()
        # 撤单模板
        recall_path = '//*[@resource-id="com.hexin.plat.android:id/chedan_listview"]' \
                      '/android.widget.LinearLayout[{}]/android.widget.LinearLayout[1]'
        for i in range(1, k + 1):
            # 点击第k单
            d.xpath(recall_path.format(1)).click()
            # 点击撤单
            d(resourceId="com.hexin.plat.android:id/option_chedan").click()
        # 返回交易主页
        d(resourceId="com.hexin.plat.android:id/title_bar_left_container").click()
        # 返回自选股页面
        d(description="自选").click()
        print("前", k, "个单，撤单完成")


def fun_timer():
    print('Hello Timer!')
    global timer
    # 24小时后再次执行
    timer = threading.Timer(86400, fun_timer)
    timer.start()


def start():
    time_to_start = " 22:56:00"
    # 获取现在时间
    now_time = datetime.datetime.now()
    now_year = now_time.date().year
    now_month = now_time.date().month
    now_day = now_time.date().day
    # 判断今天是否达到指定时间
    now_time_limit = datetime.datetime.strptime(
        str(now_year) + "-" + str(now_month) +
        "-" + str(now_day) + time_to_start,
        "%Y-%m-%d %H:%M:%S")
    if (now_time_limit - now_time).total_seconds() >= 0:
        timer_start_time = (now_time_limit - now_time).total_seconds()
        print(timer_start_time)
        timer = threading.Timer(timer_start_time, fun_timer)
        timer.start()
    else:
        # 获取明天时间
        next_time = now_time + datetime.timedelta(days=+1)
        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day
        next_time_limit = datetime.datetime.strptime(
            str(next_year) + "-" + str(next_month) +
            "-" + str(next_day) + time_to_start,
            "%Y-%m-%d %H:%M:%S")
        # 获取距离明天22点时间，单位为秒
        timer_start_time = (next_time_limit - now_time).total_seconds()
        print(timer_start_time)
        timer = threading.Timer(timer_start_time, fun_timer)
        timer.start()


if __name__ == '__main__':
    # init = 'python -m uiautomator2 init'
    # os.system(init)

    # start()

    now_time = datetime.datetime.now()

    sp = StockProcess()
    d = u2.connect('127.0.0.1:62001')

    sp.buy(d, code='600123', price=3, amount=3000)
    # sp.sell(d, code='300343', price=3.24, amount=100)
    # sp.recall_k(2)
