# -*- coding: utf-8 -*-
import re
import db
import config
import logging
import requests
from time import sleep
from parsel import Selector
from datetime import datetime
_xpath_topics = '//*[@id="ipbcontent"]/div/ol/li'
_xpath_messages = '//*[@id="print"]/div[@class="printpost"]'
_url_lofi_page = 'http://diesel.elcat.kg/lofiversion/index.php?f{0}-{1}.html'
_url_print_page = 'http://diesel.elcat.kg/index.php?act=Print&client=printer&f=1&t={0}'

logging.basicConfig(filename='ipchecker.log',level=logging.INFO)


def _grab_topics(fid):
    topics = []
    recomp = re.compile(r'\?t(?P<id>[\d]+).html\'>(?P<title>.*?)</a>', re.DOTALL)
    ids = []
    for page in range(config.forum_pages_depth):
        logging.info(str(fid) + ':' + str(page + 1))
        # lite version topics list contains 150 topics per page
        text = requests.get(_url_lofi_page.format(fid, 150 * page)).text

        for topic in recomp.finditer(text):
            id = int(topic.group('id'))
            if id not in ids:
                ids.append(id)
                topics.append({
                    'id': id,
                    'title': topic.group('title'),
                })
    return topics


def _grab_messages(topic):
    logging.info(str(topic))
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
    logging.info(str(len(msgs)) + ' messages')
    return msgs


def main():
    for fid in db.get_forum_ids():
        topics = _grab_topics(fid)
        for topic in topics:
            msgs = _grab_messages(topic['id'])
            db.process_topic(topic, fid, msgs)
            sleep(config.delay_between_requests)

