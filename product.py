import datetime


class Product:
    STATUS_INIT = "投资"
    STATUS_TRANSACTIONING = "购买中"
    STATUS_TRANSACTIONED = "购买完成"
    STATUS_TRANSACTIONFAILED = "购买失败"

    def __init__(self, name, url, rate, amount, status):
        self.name = name
        self.amount = float(amount.replace(",", ""))
        self.url = url
        self.status = None
        self.rate = float(str(rate).replace("%", ""))
        if status == '投资':
            self.status = self.STATUS_INIT
        else:
            self.status = self.STATUS_TRANSACTIONFAILED
        self.id = url.split("productId=")[-1]

    def print_self(self):
        return "name:{},amount:{},status:{},rate:{}".format(self.name, self.amount, self.status, self.rate)

    def print(self):
        # end = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        end = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%m-%d")
        return "陆金所" + self.name + " " + str(self.rate) + "% " + end + "到期   金额：" + str(self.amount) + "\r\n"
