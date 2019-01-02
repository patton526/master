from selenium import webdriver
import time

wd = webdriver.Chrome()
wd.get("https://www.baidu.com")    # 打开百度浏览器
wd.find_element_by_id("kw").send_keys("selenium")   # 定位输入框并输入关键字
wd.find_element_by_id("su").click()   #点击[百度一下]搜索
time.sleep(3)   #等待3秒
wd.quit()   #关闭浏览器

#要注意chrome与chromedriver的版本匹配，http://npm.taobao.org/mirrors/chromedriver/71.0.3578.80/