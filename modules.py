from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 遷移したページの状態を確認
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary 

import pandas as pd
import time

from abc import ABCMeta, abstractmethod
from time import sleep
import gspread
from gspread.spreadsheet import Spreadsheet
from apiclient import discovery  # pip install google-api-python-client
from google.oauth2.service_account import Credentials
from typing import Union, List, Optional
from gspread_dataframe import set_with_dataframe

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

chromedriver_puth = 'chromedriver'
df_dict = {
'アマゾン':'data_amazon',
 '楽天':'data_rakuten',
 'バリューコマース':'data_valuecomm',
 'A8':'data_a8',
 'アクトレ':'data_access',
 'afb':'data_afb',
 'フクロウ':'data_fukuro'
 }

class ASP(metaclass=ABCMeta):
  """
  ASPにログインし操作するための親クラス。
  """

  def __init__(self, asp_name, login_url, login_id, password, report_url,
              loginid_selector, password_selector, loginbutton_selector,reporttable_selector,
              
              sales_selector = None, group_selector =None, daily_selector = None, afiltate_link = None, table_id = None):
    print('in ASP init')
    self.asp_name  = asp_name
    self.login_url = login_url
    self.login_id  = login_id
    self.password  = password
    self.report_url = report_url
    # self.driver    = self.prepare_driver()
    options = webdriver.ChromeOptions()
    #参考　https://netwiz.jp/python3-web-browser/#Web-2
    # User-Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

    # オプション設定
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--user-agent=' + user_agent)
    options.add_argument('--lang=ja-JP')
    options.add_argument("--disable-dev-shm-usage")
    
    self.driver = webdriver.Chrome(options=options)
    self.driver.implicitly_wait(15)
    self.driver.set_page_load_timeout(15)
    self.driver.set_window_size('1200', '10000')

    # ログインに関するDOMを指定
    self.loginid_selector = loginid_selector
    self.password_selector = password_selector
    self.loginbutton_selector = loginbutton_selector
        
    self.reporttable_selector = reporttable_selector
    
    self.sales_selector = sales_selector
    
    self.group_selector = group_selector
    self.daily_selector = daily_selector
    self.afiltate_link = afiltate_link
    self.table_id = table_id
    
    # DataFrame
    self.result_df = None
 
  #@abstractmethod
  def login(self):
    print('in {} login'.format(self.asp_name))

    # 1-1. ログインページに遷移
    RETRIES = 3
    # 楽天の場合、ウィンドウサイズを拡大
      
    self.driver.get(self.login_url)

    # 1-2. IDを入力（要素が出現するまで最大20秒待つ）

    id_elem = WebDriverWait(self.driver, 20).until(
        EC.presence_of_element_located((By.XPATH, self.loginid_selector))
    ).send_keys(self.login_id)
    

  # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
    password_elem = WebDriverWait(self.driver, 20).until(
        EC.presence_of_element_located((By.XPATH, self.password_selector))
    ).send_keys(self.password)

    # 1-4. ログインボタンをクリ 
    login_button = self.driver.find_element_by_xpath(self.loginbutton_selector)
    try:
      login_button.click()
    except:
        pass



  #@abstractmethod
  def get_data(self):
    print('in {} get_data'.format(self.asp_name))

    # 2-1. ログイン状態でレポートページに遷移
    
    # self.driver.quit()
    self.driver.get(self.report_url)
    
      
    sleep(5)
    report_table = self.driver.find_element(by = By.XPATH,value=self.reporttable_selector)

    # 2-6. 表をpandasのDataFrameとして操作
    report_table_html = report_table.get_attribute('outerHTML')
    table_df = pd.read_html(report_table_html)[0]

    self.result_df = table_df
    # self.result_df = report_table_html
    


  @abstractmethod
  def prettify_data(self):
    '''このメソッドを子クラスでオーバーライドする
    https://stackoverflow.com/questions/44576167/force-child-class-to-override-parents-methods
    '''
    pass
  
  @abstractmethod
  def toYenInt(self, row):
    '''このメソッドを子クラスでオーバーライドする
    https://stackoverflow.com/questions/44576167/force-child-class-to-override-parents-methods
    '''
    pass

##########################################################
# A8net
class A8(ASP):
  """
  A8にログインし操作するためのクラス。
  ID/パスワードに関係するHTMLの抜粋は以下
  A8: <li class="idInput"><input type="text" name="login" autocomplete="on" value="" tabindex="1" id="asLoginId"></li>
  A8: <li class="passInput"><input type="password" autocomplete="on" name="passwd" value="" tabindex="2"></li>
  ログインボタンに関係するHTMLの抜粋は以下
  A8: <li class="lgnBtn"><input type="image" name="lgin_as_btn" src="/wp/wp-content/themes/a8theme/images/lgin_as_btn.gif" alt="ログイン" tabindex="3"></li>
  """

  def __init__(self, login_id, password):
    asp_name  = 'A8'
    print('in {} init'.format(asp_name))
    login_url = 'https://www.a8.net/'
    report_url = 'https://pub.a8.net/a8v2/media/resultReportAction/ud.do?action=ud'

    # ログインに関するDOMを指定
    loginid_selector = '//*[@id="asLoginId"]'
    password_selector = '//*[@id="headArea"]/div[1]/form/input[2]'
    loginbutton_selector = '//*[@id="headArea"]/div[1]/form/input[3]'
    
 
    reporttable_selector = '//*[@id="mainArea2clm"]/table'
    

    super().__init__(asp_name = asp_name, login_url=login_url, login_id = login_id, password=password, report_url=report_url,
                    loginid_selector=loginid_selector, password_selector=password_selector, loginbutton_selector=loginbutton_selector,
                    reporttable_selector = reporttable_selector)

  def prettify_data(self):
    print('in {} prettify_data'.format(self.asp_name))
    # （A8特有：列名を指定、ASP名追加、金額を数字に変換）
    # self.result_df['ASP'] = self.asp_name
    self.result_df = self.result_df
    
    # a8独自の処理
    self.result_df=self.result_df[:-1]
    self.result_df=self.rename_multicol(self.result_df)
    self.result_df.columns = ['日付', '総インプレッション数', '総クリック数', 'クリック報酬・クリック数',
       'クリック報酬・発生報酬額', 'アフィリエイト報酬・発生件数', 'アフィリエイト報酬・発生報酬額', '合計発生報酬額']
    for col in self.result_df.columns:
      self.result_df[col]=self.result_df[col].astype('str').str.split(pat='円', expand=True)[0]
      
    self.result_df['日付'] = pd.to_datetime(self.result_df['日付'], format = '%Y/%m/%d')
    self.result_df = self.result_df.sort_values('日付').reset_index(drop = True)  
    
    return self.result_df
    
  def rename_multicol(self, df):
    df_col=df.columns #列名をコピー
    df = df.T.reset_index(drop=False).T #一回列名をリセット
    for  i in range(df.shape[1]): #列名を新たに定義
        rename_col = {i:"".join(df_col[i])}
        df = df.rename(columns = rename_col)     
    df = df.drop(["level_0","level_1"],axis=0)
    return df
  
  def toYenInt(self, row):
    rewards = row['発生報酬額'].replace(',', '')
    pos = rewards.find(' 円')
    if pos < 0:
        rewards = int(float(rewards))
    else:
        rewards = int(float(rewards[:pos]))

    row['発生報酬額'] = rewards
    return row
#######################################################33
#フクロウ
class Fukurou(ASP):
  """
  バリューコマースにログインし操作するためのクラス。
  ID/パスワードに関係するHTMLの抜粋は以下
  <input type="email" id="login_form_emailAddress" name="login_form[emailAddress]" required="required">
  <input type="password" id="login_form_encryptedPasswd" name="login_form[encryptedPasswd]" required="required">
  ログインボタンに関係するHTMLの抜粋は以下
  <input type="submit" value="ログイン" class="btn_green">
  """

  def __init__(self, login_id, password):
    asp_name  = 'フクロウ'
    print('in {} init'.format(asp_name))
    login_url = 'https://x-dashboard.cir.io/login'
    report_url = 'https://x-dashboard.cir.io/general/media/reports/daily'

    # ログインに関するDOMを指定
    loginid_selector = '//*[@id="general_user_mail"]'
    password_selector = '//*[@id="general_user_password"]'
    loginbutton_selector = '//*[@id="login-form"]/div/input'
    
    # レポートに関するDOMを指定
    reporttable_selector = '//*[@id="DataTables_Table_0"]'


    super().__init__(asp_name = asp_name, login_url=login_url, login_id = login_id, password=password, report_url=report_url,
                    loginid_selector=loginid_selector, password_selector=password_selector, loginbutton_selector=loginbutton_selector,
                    reporttable_selector = reporttable_selector)
    

  def prettify_data(self):
    print('in {} prettify_data'.format(self.asp_name))
    self.result_df = self.result_df
    self.result_df = self.result_df[:-2]
    self.result_df['日付'] = self.result_df['日付'].str[:-3]
    self.result_df['日付']=pd.to_datetime(self.result_df['日付'])
    self.result_df= self.result_df.sort_values('日付').reset_index(drop = True)


    return self.result_df


  def toYenInt(self, row):
    rewards = int(float(row['報酬金額(税込)'].replace(',', '').replace('¥', '')))
    row['報酬金額(税込)'] = rewards
    return row

##############################################
#楽天
class Rakuten():
    
    def get_report(self):
        options = webdriver.ChromeOptions()
        #参考　https://netwiz.jp/python3-web-browser/#Web-2
        # User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

        # オプション設定
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--user-agent=' + user_agent)
        options.add_argument('--lang=ja-JP')
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(15)
        driver.set_page_load_timeout(15)


        driver.set_window_size('1200', '10000')
            
        driver.get('https://grp01.id.rakuten.co.jp/rms/nid/vc?__event=login&service_id=top')

        # 1-2. IDを入力（要素が出現するまで最大20秒待つ）

        id_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginInner_u"]'))
        ).send_keys('afb@curumi.jp')


        # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
        password_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="loginInner_p"]'))
        ).send_keys('Curumi@1031')

        # 1-4. ログインボタンをクリ 
        login_button = driver.find_element_by_xpath('//*[@id="loginInner"]/p[1]/input')
        try:
            login_button.click()
        except:
            pass
        
        sleep(3)
        driver.set_window_size('1200', '10000')
        driver.get('https://affiliate.rakuten.co.jp/report/monthly')

        report_table = driver.find_element(by = By.XPATH,value='//*[@id="monthly_report_table"]')

        report_table = pd.read_html(report_table.get_attribute('outerHTML'))[0]
        
        report_table.columns = ['日付','成果報酬','クリック数','売上件数','売上金額']
        print(report_table)
    
        try:
        
            report_table['日付']=pd.to_datetime(report_table['日付'])
        except:
            pass
        
        return report_table


##########################
#アマゾン
class Amazon():

    def get_report(self):
        options = webdriver.ChromeOptions()
        #参考　https://netwiz.jp/python3-web-browser/#Web-2
        # User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

        # オプション設定
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--user-agent=' + user_agent)
        options.add_argument('--lang=ja-JP')
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        driver.set_page_load_timeout(15)


        driver.set_window_size('1200', '10000')
        driver.get('https://www.amazon.co.jp/ap/signin?ie=UTF8&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Faffiliate.amazon.co.jp%2F&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_associates_jp&openid.mode=checkid_setup&marketPlaceId=A1VC38T7YXB528&language=ja_JP&ignoreAuthState=1&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&ie=UTF8&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&fromAuthPrompt=1')

        id_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ap_email"]'))
        ).send_keys('afb@curumi.jp')


        # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
        password_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ap_password"]'))
        ).send_keys('Curumi@1031')

        login_button = driver.find_element_by_xpath('//*[@id="signInSubmit"]')
        try:
            login_button.click()
        except:
            pass

        sleep(5)
        report_url = 'https://affiliate.amazon.co.jp/home/reports'
        

        driver.get(report_url)

        sales_selector = '//*[@id="reports-commission-earnings-header"]'
        
        driver.set_window_size('12000', '20000')
        sales_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, sales_selector)))
        
        try:    
            sales_elem.click()
        except:
            pass 


        report_table_selector = '//*[@id="ac-report-commission-simple-earnings-tbl"]/div[5]/table'

        sleep(10)
        report_table_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, report_table_selector))
        )

        report_table_html = report_table_elem.get_attribute('outerHTML')

        report_table = pd.read_html(report_table_html)[0]
        
        report_table.columns =['日付', 'クリック数', '発送済み商品数',
            '売上商品の売上額', '紹介料金額に紹介料率をかけた紹介料額']
        report_table['日付']=pd.to_datetime(report_table['日付'])
        report_table = report_table.sort_values(by='日付').reset_index(drop = True)
        
        cols = ['売上商品の売上額', '紹介料金額に紹介料率をかけた紹介料額']
        for col in cols:
            report_table[col] = report_table[col].apply(self.toYenInt)
            
        report_table['日付']=pd.to_datetime(report_table['日付'])
        
        return report_table
        
    def toYenInt(self, row):
        rewards = int(float(row.replace(',', '').replace('¥', '')))
        row = rewards
        return row

    
############################################################################
#afb

class Afb():
    def get_report(self):
        options = webdriver.ChromeOptions()
        #参考　https://netwiz.jp/python3-web-browser/#Web-2
        # User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

        # オプション設定
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--user-agent=' + user_agent)
        options.add_argument('--lang=ja-JP')
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(15)
        driver.set_page_load_timeout(15)


        driver.set_window_size('1200', '10000')
        driver.get('https://www.afi-b.com/')

        id_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="formPartnerId"]'))
        ).send_keys('afbcurumi')

        # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
        password_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="formPartnerPassword"]'))
        ).send_keys('curumi1031')


        login_button = driver.find_element_by_xpath('//*[@id="gatsby-focus-wrapper"]/div[1]/div[1]/div/div/div[1]/form/div[1]/div[3]/button')
        try:
            login_button.click()
        except:
            pass

        sleep(5)
        report_url = 'https://www.afi-b.com/pa/report/?r=daily#report_view'

        driver.get(report_url)

        display_selector = '//*[@id="report_form_2"]/div[1]/table[2]/tbody/tr/td[1]/p/input'
        display_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, display_selector))
        ).click()

        report_table_selector = '//*[@id="reportTable"]'

        sleep(10)
        report_table_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, report_table_selector))
        )

        report_table_html = report_table_elem.get_attribute('outerHTML')

        report_table = pd.read_html(report_table_html)[0]
        
        report_table = report_table[:-1]
        report_table.columns = ['日付', '-', '表示回数', 'Click数', 'Click報酬', 'CTR', '発生数', '発生報酬', 'CVR',
            '承認数', '承認報酬', '承認率', '未承認数', '未承認報酬', '報酬合計']
        report_table = report_table[['日付', '表示回数', 'Click数', 'Click報酬','発生数', '発生報酬',
            '承認数', '承認報酬', '未承認数', '未承認報酬', '報酬合計']]
        report_table['日付']=pd.to_datetime(report_table['日付'])
        cols = ['Click報酬', '発生報酬','承認報酬','未承認報酬','報酬合計']
        for col in cols:
            report_table[col] = report_table[col].apply(self.toYenInt)
            
        return report_table
            
    def toYenInt(self, row):
        rewards = int(float(row.replace(',', '').replace('¥', '')))
        row = rewards
        return row

        
################################################################
#バリューコマース
class ValueCommerce():
    
    def get_report(self):
        options = webdriver.ChromeOptions()
        #参考　https://netwiz.jp/python3-web-browser/#Web-2
        # User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

        # オプション設定
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--user-agent=' + user_agent)
        options.add_argument('--lang=ja-JP')
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        driver.set_page_load_timeout(15)

        driver.set_window_size('1200', '10000')
        driver.get('https://www.valuecommerce.ne.jp/')

        # （バリューコマース特有：iframeに切り替え）
        iframe = driver.find_element_by_xpath('//*[@id="frame1"]')
        driver.switch_to.frame(iframe)

        id_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login_form_emailAddress"]'))
        ).send_keys('info@dot-a.co.jp')


        # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
        password_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login_form_encryptedPasswd"]'))
        ).send_keys('Dt11dt11')

        login_button = driver.find_element_by_xpath('//*[@id="login_aff"]/input[1]')
        try:
            login_button.click()
        except:
            pass

        driver.switch_to.default_content()

        sleep(5)
        report_url = 'https://aff.valuecommerce.ne.jp/report/stats'

        driver.get(report_url)


        site_select_selector = '//*[@id="globalHeader"]/nav/div[3]/div/span/div/span'#クリック
        netr_selector = '//*[@id="ネットR"]/span[2]'
        job_media_selector = '//*[@id="しごとメディア"]/span[2]'
        meneyr_selector = '//*[@id="マネーR"]/span[2]'
        monocil_selector = '//*[@id="モノシル"]/span[1]/span'#モノシルをクリック
        click_any ='//*[@id="report"]/div[3]/div[2]/div[1]/ul/li[3]/label'#適当なところをクリック


        #サイトの選択
        site_select_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, site_select_selector))
        ).click()

        #ネットRを選択
        sleep(3)
        netr_all_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, netr_selector))
        )
        try:
            netr_all_elem.click()
        except:
            pass
        #ジョブメディアを選択
        sleep(1)
        job_media_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, job_media_selector))
        )

        try:
            job_media_elem.click()
        except:
            pass
        
        #マネーRを選択
        sleep(1)
        meneyr_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, meneyr_selector))
        )
        
        try:
            meneyr_elem.click()
        except:
            pass

        #どこかクリックしてアプライ
        any_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, click_any))
        ).click()

        report_table_selector = '//*[@id="report"]/div[4]/div[1]/div/div[3]/table'

        sleep(10)
        report_table_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, report_table_selector))
        )

        report_table_html = report_table_elem.get_attribute('outerHTML')

        report_table = pd.read_html(report_table_html)[0]

        report_table = report_table[[0, 1, 2, 4, 5, 7, 8]]
        report_table.columns = ['日付','表示回数','クリック数','注文数','注文金額','承認数','報酬合計']
        report_table['日付']=pd.to_datetime(report_table['日付'])
        report_table =report_table.sort_values('日付').reset_index(drop =True)

        cols = ['注文金額','報酬合計']
        for col in cols:
            report_table[col] = report_table[col].apply(self.toYenInt)
            
        return report_table
    def toYenInt(self, row):
        rewards = int(float(row.replace(',', '').replace('¥', '')))
        row = rewards
        return row


################################################################
#アクセストレード
class AccessTrade():
    def get_report(self):
        options = webdriver.ChromeOptions()
        #参考　https://netwiz.jp/python3-web-browser/#Web-2
        # User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"

        # オプション設定
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--user-agent=' + user_agent)
        options.add_argument('--lang=ja-JP')
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        driver.set_page_load_timeout(15)

        driver.set_window_size('1200', '10000')
        driver.get('https://www.accesstrade.ne.jp/')

        # （バリューコマース特有：iframeに切り替え）
        # iframe = driver.find_element_by_xpath('//*[@id="frame1"]')
        # driver.switch_to.frame(iframe)

        id_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/header/div[1]/div[2]/div[3]/div/form/input[1]'))
        ).send_keys('afb@curumi.jp')


        # 1-3. パスワードを入力（要素が出現するまで最大20秒待つ)
        password_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="top"]/header/div[1]/div[2]/div[3]/div/form/input[2]'))
        ).send_keys('Curumi@1031')

        login_button = driver.find_element_by_xpath('//*[@id="top"]/header/div[1]/div[2]/div[3]/div/form/input[3]')
        try:
            login_button.click()
        except:
            pass

        sleep(5)
        report_url = 'https://member.accesstrade.net/atv3/report/daily.html'

        driver.get(report_url)

        this_month_selector = '//*[@id="report"]/section/div[2]/dl[1]/dd[3]/p/a[1]'
        display_button ='//*[@id="search_btn"]'

        #「今月」をクリック
        this_month_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, this_month_selector))
        ).click()

        #「表示」をクリックしてアプライ
        any_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, display_button))
        ).click()

        report_table_selector = '//*[@id="result_box"]/table'

        sleep(8)
        report_table_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, report_table_selector))
        )

        report_table_html = report_table_elem.get_attribute('outerHTML')

        report_table = pd.read_html(report_table_html)[0]

        report_table=report_table[1:]
        report_table.columns = ['日付', '表示回数', 'クリック数', '発生件数', '発生報酬', '確定件数', '確定報酬']

        cols = ['クリック数', '発生件数', '確定件数']
        for col in cols:
            report_table[col]=report_table[col].str.split(' ', expand = True)[0]
            
        report_table['日付'] = report_table['日付'].str[:-3]
        report_table['日付']=pd.to_datetime(report_table['日付'])
        report_table= report_table.sort_values('日付').reset_index(drop = True)

        cols = ['発生報酬','確定報酬']
        for col in cols:
            report_table[col] = report_table[col].apply(self.toYenInt)
            
        return report_table
    
    def toYenInt(self, row):
        rewards = int(float(row.replace(',', '').replace('￥', '')))
        row = rewards
        return row

###############################
#各ASPのインスタンスを作成する
def asp_instance(asp_name, login_id, password):
    if asp_name == 'A8':
        return A8(login_id, password)
    elif asp_name == 'バリューコマース':
        return ValueCommerce()
    elif asp_name == 'フクロウ':
        return Fukurou(login_id, password)
    elif asp_name == 'アマゾン':
        return Amazon()
    elif asp_name == '楽天':
        return Rakuten()
    elif asp_name == 'afb':
        return Afb()
    elif asp_name == 'アクトレ':
        return AccessTrade()
    else:
        raise ValueError('Invalid ASP name: {}'.format(asp_name))
    
################################################################
#スプレッドシートの書き込み用

class GSheets:
    def __init__(self, key):
        """
        Inputs:
            - creds: the path to the credentials file for the Google Services Account.
        Attributes:
            - gc: google spreadsheet client. Use to get `gspread` convenience methods.
            - api: google api client using the apiclient.discovery module from `google-api-python-client`. Use for lower level configurations.
            - last_sheets_url: a url reference to the last processed Google Sheets.
        """
        self.sh = self.get_sh(key)
        
    def get_sh(self, key):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            'py-tools-341712-6978522c6ff8.json',
            scopes=scopes
        )

        gc = gspread.authorize(credentials)
        # gc = gspread.authorize(self.creds)
        # key = '1uC9PrJIQcxUQq4NfM-x5hlf2MfmBOehMFfssJ0MYvhQ'

        sh = gc.open_by_key(key)
        
        return sh
        
    
        ######　スプレッドシートのシート名を取得#########
    def get_sheet_name(self):
        worksheets = self.sh.worksheets()
        # 現在のワークシートのタイトルをリストへ格納
        tmp_worksheets_title_list = [worksheet.title for worksheet in worksheets]
        return tmp_worksheets_title_list
    
   ### 検索KWを追加###
    def add_sheet(self, date):
        ws = self.sh.add_worksheet(title=date, rows=1000, cols=20)
        return  ws
    
    ###### gsheet からのデータ取得######

    def get_data_gsh(self, date):
        tmp_worksheets_title_list = self.get_sheet_name()
        SP_SHEET = date
        if date not in tmp_worksheets_title_list:
            ws = self.add_sheet(date)
            
        ws = self.sh.worksheet(SP_SHEET)

        data = ws.get_all_values()
        
        if len(data) == 0:
            df_gsh = pd.DataFrame()
        else:
            df_gsh = pd.DataFrame(data[1:], columns = data[0])
        
        return ws, df_gsh
    
    ###### データの書き込み###########

    def return_data(self,phrase, df: Optional[pd.DataFrame]):
        ws, df_gsh = self.get_data_gsh(phrase)
        
        if len(df_gsh) > 0:
            #日付の確認
            df_gsh['日付'] = pd.to_datetime(df_gsh['日付'])
            old_month=df_gsh['日付'].tail(1).item().month
            new_month = df['日付'].tail(1).item().month

            if old_month == new_month:
                df_merge = df
            else:
                df_merge=pd.concat([df_gsh,df])
                df_merge['日付']=pd.to_datetime(df_merge['日付'])
                df_merge=df_merge.sort_values('日付').reset_index(drop = True)

    
            # append_df = pd.concat([df_gsh, df])
        else:
            df_merge = df
            
        try:
            set_with_dataframe(ws, df_merge, row = 1, col = 1)
        except:
            print('データが取得できませんでした')
            
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


def get_daliy_sales(asp_name):
    my_asp = asp_instance(asp_name, credentials[asp_name]['login_id'], credentials[asp_name]['password'])
    
    if (asp_name == 'アマゾン') or (asp_name == '楽天')or (asp_name == 'afb')or (asp_name == 'バリューコマース')or (asp_name == 'アクトレ'):
        table_df = my_asp.get_report()
        
    else:
        my_asp.login()
        my_asp.get_data()
        table_df = my_asp.prettify_data()
    
    print(table_df)
    this_date = table_df['日付'].head(1).item().strftime('%Y-%m')
    
    gs = GSheets(key_dict[asp_name])
    gs.return_data(this_date, table_df)
    
    return table_df

