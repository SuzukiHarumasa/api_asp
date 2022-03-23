import streamlit as st
from PIL import Image
#-*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time

#自作モジュールのインポート
from modules import ASP,A8,Fukurou,Rakuten,Amazon,Afb,ValueCommerce,AccessTrade,asp_instance,GSheets,get_daliy_sales

amazon_key = '1LvQFK8cHl8ogFVJVa9PhOFtO05gfR-7_dOJaiLucBew'
rakuten_key = '1A5vJkEKNG1IBHXN2oUioDlQtXJEfLCEVMSJ7DMxdaKc'
valuecomm_key = '1kI0sZayd0yA0EuzIlVOQ4zcwwAX1_mdK2y-YCPb718o'
a8_key = '1haELIWmh_XQwfIGus9PdBLcfk6ag98EwkEQ_p-aweZ4'
access_key = '1sP2xLRNJHMwuLkuqwlCtSqBKDejV6Q_SZpD3W9rwCC8'
afb_key = '18Mpz4awzeV9Yfzmsg9p5QxEgv6LucsPBhOnNRk_ie3U'
fukuro_key = '16odHyCzbgwk9r5eaN7pocqkVFL-rNEcqe00EkvGDN9M'

key_dict = {

 '楽天':rakuten_key,
 'バリューコマース':valuecomm_key,
 'A8':a8_key,
 'アクトレ':access_key,
 'afb':afb_key,
 'フクロウ':fukuro_key,
 'アマゾン':amazon_key,
 }

df_dict = {
 '楽天':'data_rakuten',
 'バリューコマース':'data_valuecomm',
 'A8':'data_a8',
 'アクトレ':'data_access',
 'afb':'data_afb',
 'フクロウ':'data_fukuro',
 'アマゾン':'data_amazon',
 }

piyotaso = Image.open('./static/piyotaso.png')
piyotaso_uresi = Image.open('./static/piyotaso_uresi.png')

st.write('# ASP自動更新ツールです〜')
button = st.button('クリックしてください〜')
st.image(piyotaso,width=300)

if button:
    asps = df_dict.keys()
    for asp_name in asps:
        df_ = get_daliy_sales(asp_name)
    
    st.write('更新完了！')
    st.image(piyotaso_uresi,width=300)
     
else:
    pass