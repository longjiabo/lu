import datetime


class Product:
    STATUS_INIT = "购买队列中"
    STATUS_TRANSACTIONING = "购买中"
    STATUS_TRANSACTIONED = "购买完成"
    STATUS_TRANSACTIONFAILED = "购买失败"

    def __init__(self, name, url, rate, amount):
        self.name = name
        self.amount = float(amount.replace(",", ""))
        self.url = url
        self.status = None
        self.rate = float(str(rate).replace("%", ""))
        self.status = self.STATUS_INIT
        self.id = url.split("productId=")[-1]

    def print(self):
        #end = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        end = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m-%d")
        return "陆金所" + self.name + " " + str(self.rate) + "% " + end + "到期   金额：" + str(self.amount) + "\r\n"
