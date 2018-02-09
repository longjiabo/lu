import json
import queue
import threading

import requests
from bs4 import BeautifulSoup

import constant
from captcha import Captcha
import log


class Transaction(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user
        self.products = []
        self.transactionQueue = queue.Queue()
        self.session = requests.session()
        if constant.proxy:
            constant.set_proxy(self.session)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
        self.session.verify = False
        self.product = None
        self.is_waitting = False

    def run(self):
        while True:
            self.is_waitting = True
            product = self.transactionQueue.get()
            if product is None:
                break
            self.product = product
            self.is_waitting = False
            self.action()

    def login(self):
        res = self.session.get("https://user.lu.com/user/login")
        captcha = None
        if res.status_code == 200:
            captcha = Captcha(self.session.get(constant.loginCaptcha).content, None)
            captcha.requestCaptcha()
        data = {
            "isTrust": 'Y',
            "password": self.user.loginPassword,
            "openlbo": 0,
            "deviceKey": constant.device['deviceKey'],
            "deviceInfo": constant.device['deviceInfo'],
            "loginFlag": 1,
            "hIsOpenLboAccStatus": 0,
            "hIsSignLboUserCrsChecked": 0,
            "userName": self.user.username,
            "pwd": self.user.loginPassword,
            "validNum": captcha.result,
            "agreeLbo": "on",
            "loginagree": "on"
        }
        res = self.session.post(constant.loginUrl, data=data)
        log.info(res.text)
        o = res.json()
        if 'resultMsg' in o and o['resultMsg'] == 'MISS_VCODE':
            self.login()
        self.parseLoginInfo(o)

    def parseLoginInfo(self, o):
        self.user.userId = o['userId']
        self.user.token = o['token']
        self.getAmount()
        log.info("amount:" + str(self.user.amount))

    def getAmount(self):
        res = self.session.get(constant.accountUrl)
        soup = BeautifulSoup(res.text, "html.parser")
        span = soup.select_one(".account-balance-item .coin-point-item-number")
        span2 = soup.select_one(".lujinbao-balance-information .coin-point-item-number")
        self.user.amount = float(span.text.replace(",", ""))
        self.user.amount = self.user.amount + float(span2.text.replace(",", ""))

    def isLogin(self):
        res = self.session.get(constant.accountUrl)
        return len(res.history) < 3

    def action(self):
        self.product.status = self.product.STATUS_TRANSACTIONING
        if not self.isLogin():
            self.login()
        self.processing()

    def getSid(self):
        res = self.session.post("https://list.lu.com/list/itrading/invest-check",
                                data={"productId": self.product.id,
                                      "investAmount": self.product.amount,
                                      "investSource": 0,
                                      "isCheckSQ": 1})
        log.info("sid:" + res.text)
        o = res.json()
        sid = None
        if o['res_code'] == '66':
            sid = o['data']['sid']
            sid = str(sid)
        self.sid = sid

    def clickNext(self, step):
        self.session.post("https://trading.lu.com/trading/i-sendStep",
                          data={'curStep': step, 'productId': self.product.id, 'sid': self.sid})
        # print("点击下一步", res.text)

    def getBuyCaptcha(self):
        res = self.session.post("https://trading.lu.com/trading/service/trade/captcha/create-captcha",
                                data={'sid': self.sid, 'productId': self.product.id})
        log.info(res.text)
        o = json.loads(res.text)
        if o['retCode'] != '00':
            return
        imageId = o['imageId']
        captchaUrl = "https://user.lu.com/user/captcha/get-captcha?source=1&imageId=" + imageId
        captcha = Captcha(self.session.get(captchaUrl).content, imageId)
        captcha.requestCaptcha()
        return captcha

    def processing(self):
        log.info("https://list.lu.com" + self.product.url + " amount:" + str(self.product.amount))

        # 获取sid
        self.getSid()
        if not self.sid:
            self.product.status = self.product.STATUS_TRANSACTIONFAILED
            return
        self.clickNext("TRADE_INFO")
        self.clickNext("CONTRACT")
        captcha = self.getBuyCaptcha()
        res = self.session.post("https://trading.lu.com/trading/service/trade/trace",
                                {'curStep': 'OTP', 'productId': self.product.id, 'sid': self.sid})
        log.info(res.text)
        data = {
            'sid': self.sid,
            'productId': self.product.id,
            'source': 0,
            'coinString': '',
            'needWithholding': 'false',
            # 1 默认值 余额
            # 2 银行卡
            # 6 默认值+陆金宝
            'paymentMethod': 6,
            'password': self.user.payPassword,
            'isSetPassword': 0,
            'captcha': captcha.result,
            'imgId': captcha.imageId
        }
        res = self.session.post("https://trading.lu.com/trading/i-investment-request", data)
        log.info(res.text)
        o = res.json()
        if o['res_code'] == '01':
            self.product.status = self.product.STATUS_TRANSACTIONED
            self.product.trxId = o['data']['trxId']
            self.product.investmentRequestId = o['data']['investmentRequestId']
            self.products.append(self.product)
            self.user.amount = self.user.amount - self.product.amount
        else:
            self.product.status = self.product.STATUS_TRANSACTIONFAILED
