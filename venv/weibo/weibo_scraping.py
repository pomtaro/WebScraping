
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from WeiboCrawler import Crawler

import time

# リストを準備
account_names = []
feed_times = []
sentences = []
shares = []
comments = []
goods = []
ranks = []
locations = []
genders = []
follows = []
followers = []
weiboes = []
get_times = []
types = []

comment_account_names = []
comment_sentences = []
comment_types = []
# コメントについては、下記情報は一旦保留
comment_locations = []
comment_genders = []
comment_ranks = []
comment_follows = []
comment_followers = []
comment_weiboes = []
comment_post_times = []
comment_get_times = []
comment_shares = []
comment_comments = []
comment_goods = []

# クローラー初期化
crawler = Crawler()

# driver定義
driver = crawler.set_driver()

# 初期ページ定義
start_url = 'https://s.weibo.com/weibo?q=toyota&wvr=6&b=1&display=0&retcode=6102&Refer=SWeibo_box'

# 初期ページ遷移
driver.get(start_url)

# weiboログインのため待機
time.sleep(20)

# 初期ページから最終ページまでページリンクを取得
feed_links = crawler.get_feed_links(start_url)

# クロール本体
# フィードページごとにデータ取得
for i, feed_link in enumerate(feed_links):
    # フィード全体のhtml_soupを取得
    feed_html_soup = crawler.get_feed_html_soup(driver, feed_link)

    # フィードの投稿ID(=mid)を取得
    mids = crawler.get_mid_list(feed_html_soup)

    # 各フィード(mid)ごとにデータを取得
    for j, mid in enumerate(mids):
        # アカウントページリンクを取得
        account_link = 'https:' + crawler.get_account_link(feed_html_soup, mid)

        # フィードのデータを取得
        account_name, feed_time, sentence, share, comment, suda_data, good = crawler.get_feed_info(feed_html_soup, mid)

        # フィードに対するコメントを取得する場合は、ここで追加処理 -> jupyter notebook参照

        # アカウント詳細のhtml_soupを取得
        account_html_soup = crawler.get_account_html_soup(driver, account_link)

        # アカウントデータを取得
        rank, location, gender, follow, follower, weibo, get_time = crawler.get_account_info(account_html_soup)

        # データtypeを定義
        type_name = 'feed'

        # データをリストに格納
        account_names.append(account_name)
        feed_times.append(feed_time)
        sentences.append(sentence)
        shares.append(share)
        comments.append(comment)
        goods.append(good)
        ranks.append(rank)
        locations.append(location)
        genders.append(gender)
        follows.append(follow)
        followers.append(follower)
        weiboes.append(weibo)
        get_times.append(get_time)
        types.append(type_name)

    print('progress... : {} %'.format((i + 1)/len(feed_links)*100))

# データをcsv出力
os.chdir('/Users/higashi/PycharmProjects/WeiboScraping/venv/data')
df = pd.DataFrame({
    'Account': account_names,
    'Location': locations,
    'Gender': genders,
    'Rank': ranks,
    'Follow': follows,
    'Follower': followers,
    'Weibo': weiboes,
    'FeedTime': feed_times,
    'GetTime': get_times,
    'Type': types,
    'Sentence': sentences,
    'Share': shares,
    'Comment': comments,
    'Good': goods
})
df.to_csv('data_tmp' + '.csv')
