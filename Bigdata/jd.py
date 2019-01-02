# -*- coding: utf-8 -*-
__author__ = 'EasouChen'

# 导入以下模块
# selenium用于结合phantomjs
from selenium import webdriver
import time
from lxml import etree

# 底下这行用于自定义头部文件
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pymysql

# 多进程池，用于多进程
from multiprocessing import Pool

# 使用该函数将中文转换成url参数
from urllib.parse import quote

# 这三行用于解决mysql报ascii无法decode的问题，意思是将所有字符格式default为'utf-8'
import importlib,sys
importlib.reload(sys)


# 定义函数，参数为页数
def get_goods(key, page_num):
    '''
        用于爬取京东'零食类商品信息，包括标题，价格，评论，详细页链接，店名，店铺链接'
    :param key: 爬取的关键字，如手机
    :param page_num: 第几页
    :return:
    '''
    # 链接数据库
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='root', db='jd', use_unicode=True, charset="utf8")

    # 自定义userAgent,并使用该参数访问页面
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap['phantomjs.page.settings.userAgent'] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0")
    driver = webdriver.PhantomJS(desired_capabilities=dcap)

    # 注意链接经过url处理，原因是phantomjs对url中的中文识别成了??，无法正常处理
    # 该网址中的%E9%9B%B6%E9%A3%9F 可自定义搜索条件，并使用urllib转换
    driver.get('https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=1.his.0.0' % (
        key) + '&page=%s&s=57&click=0' % (page_num * 2 - 1))

    # 打开页面后，等待两秒，下拉到页面底部，做二次加载
    js = "window.scrollTo(0,document.body.scrollHeight);"
    time.sleep(2)
    driver.execute_script(js)
    time.sleep(4)

    # 将网页数据初始化，用lxml模块处理
    htmls = etree.HTML(driver.page_source)

    # 获取商品列表
    goods_list = htmls.xpath("//div [@id='J_goodsList']/ul/li")
    count = 1
    for item in goods_list:
        # 遍历商品列表，从列表中得到每个商品的具体信息
        try:
            title1 = item.xpath("./div/div[contains(@class,'p-name')]/a/em")[0]
            title = title1.xpath("string(.)")
            print
            title
            title = title.replace('(', '<').replace(')', '>')
            price = item.xpath("./div/div[@class='p-price']/strong/i/text()")
            comment = item.xpath("./div/div[@class='p-commit']/strong/a/text()")
            link = "https:" + item.xpath("./div/div[@class='p-img']/a/@href")[0]
            shop_name = item.xpath("./div/div[@class='p-shop']//a/text()")
            if shop_name:
                shop_link = "http:" + item.xpath("./div/div[@class='p-shop']//a/@href")[0]
            else:
                shop_name = ['京东自营']
            print('\n商品' + str(count) + ':')
            print("-------------------------------------------------------")
            # print title
            # print price[0]
            # print comment[0]
            # print link
            # print shop_name[0]
            # print shop_link

            # 查找数据库中是否存在当前商品的链接
            serch_str = "select * from goods where link='%s';" % link
            ser_result = conn.query(serch_str)

            # 商品信息存入数据库
            if not ser_result:
                print('开始存储')
                if shop_name:
                    save_str = "insert into goods(title,price,comment,link,shop_name,shop_link) values('" + title + "','" + \
                               price[0] + "','" + comment[0] + "','" + link + "','" + shop_name[
                                   0] + "','" + shop_link + "');"
                else:
                    save_str = "insert into goods(title,price,comment,link,shop_name,shop_link) values('" + title + "','" + \
                               price[0] + "','" + comment[0] + "','" + link + "','" + "京东自营" + "','" + "" + "');"
                save_result = conn.query(save_str)
                conn.commit()
                print(title, '存储成功')
            else:
                print("商品已存在")
            print('-------------------------------------------------------')
            count += 1
        except Exception as e:
            print(e)

    # 关闭数据库，关闭当前页面，退出phantomjs
    conn.close()
    driver.close()
    driver.quit()
    print('第' + str(page_num) + '页', '共' + str(count) + '条记录')


# 主入口函数
if __name__ == '__main__':
    # 定义要查找的关键字，并转换成url地址参数
    key = quote('手机')

    # 定义进程池，同时运行的进程数量为4个
    po_li = Pool(4)
    # 初始化进程
    for x in range(1, 2):
        print('开始第' + str(x) + '页的进程')
        t = po_li.apply_async(get_goods, (key, x,))

    # 关闭进程池
    po_li.close()
    po_li.join()





