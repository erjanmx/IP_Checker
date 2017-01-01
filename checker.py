# -*- coding: utf-8 -*-
import re
import db
import config
import requests
from time import sleep
from parsel import Selector
from datetime import datetime

_xpath_topics = '//*[@id="ipbcontent"]/div/ol/li/a'
_xpath_messages = '//*[@id="print"]/div[@class="printpost"]'
_url_lofi_page = 'http://diesel.elcat.kg/lofiversion/index.php?f{0}-{1}.html'
_url_print_page = 'http://diesel.elcat.kg/index.php?act=Print&client=printer&f=1&t={0}'


def _grab_topics(fid):
    topics = []
    for page in range(config.forum_pages_depth):
        print str(fid) + ':' + str(page + 1)
        # lite version topics list contains 150 topics per page
        text = requests.get(_url_lofi_page.format(fid, 150 * page)).text
        selector = Selector(text=text)
        t = selector.xpath(_xpath_topics).re(r'\?t([\d]+).html')
        if not t:
            break
        topics.extend(t)
        sleep(config.delay_between_requests)
    return set(topics)


def _grab_messages(topic):
    print str(topic),
    text = requests.get(_url_print_page.format(topic)).text
    selector = Selector(text=text)
    recomp = re.compile(r'<b>(?P<author>.*?)</b>\s\s(?P<day>[\d]{1,2}).(?P<month>[\d]{1,2}).(?P<year>[\d]{4}),'
                        r'\s(?P<hour>[\d]{1,2}):(?P<minute>[\d]{1,2})</h4>',
                        re.DOTALL)
    msgs = []
    divs = selector.xpath(_xpath_messages).extract()
    for div in divs:
        data = recomp.search(div)
        if data:
            # not every message has an id
            attachment = re.search('<!--IBF.ATTACHMENT_(?P<id>[\d]+)', div)
            msgs.append({
                'id': int(attachment.group('id')) if attachment else None,
                'author': data.group('author'),
                'created_at': str(datetime(int(data.group('year')), int(data.group('month')), int(data.group('day')),
                                           int(data.group('hour')), int(data.group('minute')))),
            })
    print str(len(msgs)) + ' messages'
    return msgs


def main():
    for fid in db.get_forum_ids():
        topics = _grab_topics(fid)
        for topic in topics:
            msgs = _grab_messages(topic)
            db.process_topic(topic, msgs)
            sleep(config.delay_between_requests)

