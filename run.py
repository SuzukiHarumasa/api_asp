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