
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time


class Crawler:

    def set_driver(self):
        """
        arg: None
        return: driver
        """
        options = Options()

        # options.set_headless(True)
        options.binary_location = "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
        # options.add_argument("--headless")

        chromedriver_path = "/Users/higashi/Desktop/Document/chromedriver/chromedriver"

        return webdriver.Chrome(options=options, executable_path=chromedriver_path)

    def get_feed_html_soup(self, driver, url):
        """
        arg: url
        return: html
        """
        driver.get(url)
        html = driver.page_source.encode('utf-8')
        html_soup = BeautifulSoup(html, "html.parser")

        return html_soup

    def get_mid_list(self, html_soup):
        """
        arg: html_soup
        return: mid_list
        """
        mid_list = []
        div_elements = html_soup.find_all('div', {'id': 'pl_feedlist_index'})
        div_elements = div_elements[0].find_all('div', {'class': 'card-wrap'})
        for elem in div_elements:
            mid = elem.get('mid')
            if type(mid) == str:
                mid_list.append(mid)

        return mid_list

    def get_feed_info(self, html_soup, mid):
        """
        arg: mid
        return: account_name, feed_time, sentence, share, comment, good
        """
        div_mid = html_soup.find_all('div', {'mid': mid})

        # アカウント名
        account_name = div_mid[0].find('p').get('nick-name')

        # 時刻
        feed_time = ''.join(div_mid[0].find_all('p', {'class': 'from'})[0].find('a').text.split())
        try:
            if '今天' in feed_time:
                feed_time = dt.strftime(dt.now(), '%Y-%m-%d ') + feed_time.split('今天')[1] + ':00'
            elif '前' in feed_time:
                feed_time = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')
            elif '秒' in feed_time:
                feed_time = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')
            elif len(feed_time) < 12:
                feed_time = dt.strptime(feed_time, '%m月%d日%H:%M').replace(year=2019)
            else:
                feed_time = dt.strptime(feed_time, '%Y年%m月%d日%H:%M')
        except:
            feed_time = 'not detected'
        # 本文
        sentence = ''.join(div_mid[0].find('p').text.split())

        # シェア、コメント、いいね
        share = ''
        comment = ''
        suda_data = ''
        good = ''
        bottom_items = div_mid[0].find_all('div', {'class': 'card-act'})[0].find_all('li')
        for bottom_item in bottom_items:

            if bottom_item.text == '收藏':
                pass
            elif '转发' in bottom_item.text:
                if len(bottom_item.text.split()) < 2:
                    share = '0'
                else:
                    share = bottom_item.text.split()[1]
            elif '评论' in bottom_item.text:
                if len(bottom_item.text.split()) < 2:
                    comment = '0'
                else:
                    comment = bottom_item.text.split()[1]
                    suda_data = bottom_item.find_all('a')[0].get('suda-data')
            else:
                if len(bottom_item.text.split()) < 1:
                    good = '0'
                else:
                    good = bottom_item.text

        return account_name, feed_time, sentence, share, comment, suda_data, good

    def get_comment_id_list(self, html_soup):
        """
        arg: html_soup
        return: comment_id_list
        """
        comment_id_list = []
        div_elements = html_soup.select('div')

        for elem in div_elements:
            comment_id = elem.get('comment_id')
            if type(comment_id) == str:
                comment_id_list.append(comment_id)

        return comment_id_list

    def get_comment_name_sentence(self, html_soup, comment_id):
        """
        arg: comment_id
        return: comment_account_name, comment_text
        """
        div_comment = html_soup.find_all('div', {'comment_id': comment_id})
        comment_account_name = div_comment[0].find('div', {'class': 'txt'}).text.split()[0]
        comment_sentence = ''
        if len(div_comment[0].find('div', {'class': 'txt'}).text.split()) == 3:
            comment_sentence = div_comment[0].find('div', {'class': 'txt'}).text.split()[2]
        elif len(div_comment[0].find('div', {'class': 'txt'}).text.split()) == 2:
            comment_sentence = 'None or emoji'
        return comment_account_name, comment_sentence

    def get_account_link(self, html_soup, mid):
        """
        arg: html_soup, mid
        return: account_link
        """
        div_mid = html_soup.find_all('div', {'mid': mid})
        time.sleep(1)
        account_link = div_mid[0].find_all('a', {'class': 'name'})[0].get('href')

        return account_link

    def get_account_html_soup(self, driver, account_link):
        """
        arg: account_link
        return: html_soup
        """
        driver.get(account_link)
        time.sleep(5)  # 3sだとデータが取りきれない場合がある

        html = driver.page_source.encode('utf-8')
        html_soup = BeautifulSoup(html, "html.parser")

        return html_soup

    def get_account_info(self, html_soup):
        """
        arg: html_soup
        return: rank, location, gender, follow, follower, weibo, get_time
        """
        rank = self.get_rank(html_soup)
        location = self.get_location(html_soup)
        gender = self.get_gender(html_soup)
        follow, follower, weibo = self.get_follow_follower_weibo(html_soup)
        get_time = self.get_now_time()

        return rank, location, gender, follow, follower, weibo, get_time

    def get_rank(self, html_soup):
        """
        arg: html_Soup
        return: rank
        """
        span_all = html_soup.find_all('span')

        rank = ''

        for span_tag in span_all:
            if "Lv" in span_tag.text:
                rank = span_tag.text

        if rank == '':
            rank = 'no rank'

        return rank

    def get_location(self, html_soup):
        """
        arg: html_soup
        return: location
        """
        if html_soup.find_all('em', {'class': 'W_ficon ficon_cd_place S_ficon'}):
            span = html_soup.find_all('span', {'class': 'item_text W_fl'})

            location = ''

            for tag in span:
                if 'Lv' in tag.text:
                    location = span[1].text.split()
                    break
                else:
                    location = span[0].text.split()

            if type(location) == list:
                word_concat = ''
                for word in location:
                    word_concat += word
                location = word_concat
        else:
            location = 'no location'

        return location

    def get_gender(self, html_soup):
        """
        arg: html_soup
        return: gender
        """
        if html_soup.find_all('i', {'class': 'W_icon icon_pf_male'}):
            gender = 'male'
        elif html_soup.find_all('i', {'class': 'W_icon icon_pf_female'}):
            gender = 'female'
        else:
            gender = 'no gender'

        return gender

    def get_follow_follower_weibo(self, html_soup):
        """
        arg: html_soup
        return: follow, follower, weibo
        """
        if html_soup.find_all('strong'):
            strongs = html_soup.find_all('strong')
            try:
                follow = strongs[0].text
            except:
                follow = 'no follow'

            try:
                follower = strongs[1].text
            except:
                follower = 'no follower'

            try:
                weibo = strongs[2].text
            except:
                weibo = 'no weibo'
        else:
            follow = 'no follow'
            follower = 'no follower'
            weibo = 'no weibo'

        return follow, follower, weibo

    def get_now_time(self):
        """
        arg: None
        return: now_time
        """

        now = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')

        return now

    def get_feed_links(self, start_url):
        """
        arg: url
        return: urls
        """
        urls = []
        urls.append(start_url)

        url = start_url

        for i in range(2):  # 何ページ目まで読むか
            r = requests.get(url)
            html_contents = r.text

            html_soup = BeautifulSoup(html_contents)
            try:
                next_link = 'https://s.weibo.com' + html_soup.find_all('a', {'class': 'next'})[0].get('href')
                if next_link in urls:
                    break
                else:
                    urls.append(next_link)
                    url = next_link
            except:
                break

        return urls

    def get_comment_button_list(self, driver):
        """
        arg: driver
        return: elems, elems_suda_data
        """
        elems = []
        elems_suda_data = []

        element = driver.find_elements_by_tag_name('a')
        for elem in element:
            val_string = elem.get_attribute('action-type')
            try:
                if val_string == 'feed_list_comment':
                    elems.append(elem)
                    elems_suda_data.append(elem.get_attribute('suda-data'))
            except:
                pass

        return elems, elems_suda_data

    def click_comment(self, suda_data, elems, elems_suda_data):
        """
        arg: suda_data, elems, elems_suda_data
        return: None
        """
        try:
            for i, elem in enumerate(elems):
                if suda_data == elems_suda_data[i]:
                    element = elem
                    break
                else:
                    continue
            element.click()
            time.sleep(5)  # 2s程度待たないとcomment欄が表示されない(javascript実行時間)
        except:
            pass
