import queue
import threading
import time

import requests
from bs4 import BeautifulSoup

import constant
from product import Product

import log


class Scanner(threading.Thread):
    products = queue.Queue()

    def stop(self):
        self.running = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.session = requests.session()
        self.session.verify = False
        if constant.proxy:
            proxies = {"https": "http://cn-proxy.jp.oracle.com"}
            self.session.proxies = proxies
        self.running = True

    def run(self):
        while self.running:
            self.scanner()
            time.sleep(0.5)

    def scanner(self):
        r = self.session.get(constant.listUrl)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            lis = soup.select(".product-list")
            ps = []
            log.debug("test...")
            for i in lis:
                name = i.select(".product-name a")[0].text
                link = i.select(".product-name a")[0]['href']
                rate = i.select(".interest-rate p")[0].string
                amount = i.select(".product-amount .num-style")[0].text
                amount = amount.replace(",", "")
                p = Product(name, link, rate, amount)
                ps.append(p)
                log.debug(str(p.amount))
            log.debug("sort product...")
            ps.sort(key=lambda p: p.amount, reverse=True)
            for a in ps:
                log.debug(str(a.amount))
                self.products.put(a)
