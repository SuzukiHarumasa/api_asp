from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 遷移したページの状態を確認
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time

#自作モジュールのインポート
from modules import ASP,A8,Fukurou,Rakuten,Amazon,Afb,ValueCommerce,AccessTrade,asp_instance,GSheets,get_daliy_sales

#なぜか一回開かないと動かない
driver = webdriver.Chrome()
driver.close()

#アフィリエイトサイト（ASP）ごとのID

login_id_a8 = 'curumi0821' #@param {type:"string"}
login_mail_valuecommerce = 'info@dot-a.co.jp' #@param {type:"string"}
login_mail_fukurou = 'info@dot-a.co.jp'
login_mail_amazon = 'afb@curumi.jp'
login_mail_rakuten = 'afb@curumi.jp'
login_mail_afb = 'afbcurumi'
login_mail_actrade = 'info@dot-a.co.jp'

password_a8 = 'Curumi@1031'
password_valuecommerce = 'Dt11dt11'
password_fukurou = 'dotA1337'
password_amazon = 'Curumi@1031'
password_rakuten = 'Curumi@1031'
password_afb = 'curumi1031'
password_actrade = 'Dt11dt11'

credentials = dict()
credentials['A8'] = {'login_id': login_id_a8, 'password': password_a8}
credentials['バリューコマース'] = {'login_id': login_mail_valuecommerce, 'password': password_valuecommerce}
credentials['フクロウ'] = {'login_id': login_mail_fukurou, 'password': password_fukurou}
credentials['アマゾン'] = {'login_id': login_mail_amazon, 'password': password_amazon}
credentials['楽天'] = {'login_id': login_mail_rakuten, 'password': password_rakuten}
credentials['afb'] = {'login_id': login_mail_afb, 'password': password_afb}
credentials['アクトレ'] = {'login_id': login_mail_actrade, 'password': password_actrade}

key = '17luM78MU8aEOqKIOd8F7490pol1HToe0NK12K_9pEVc'
gs = GSheets(key)

df_dict = {
'アマゾン':'data_amazon',
 '楽天':'data_rakuten',
 'バリューコマース':'data_valuecomm',
 'A8':'data_a8',
 'アクトレ':'data_access',
 'afb':'data_afb',
 'フクロウ':'data_fukuro'
 }

asps = df_dict.keys()
for asp_name in asps:
    df_ = get_daliy_sales(asp_name)