import urllib3
from scanner import Scanner
from transaction import Transaction

import log, constant

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

scannerWorkers = []
transactionWorkers = []
products = []


# 结束所有线程
def stop():
    for scanner in scannerWorkers:
        scanner.stop()
        scanner.join()
    for txn in transactionWorkers:
        txn.transactionQueue.put(None)
        txn.join()


# 启动扫描和交易线程
def start():
    log.info("start...")
    for u in getUsers():
        txn = Transaction(u)
        txn.login()
        txn.start()
        transactionWorkers.append(txn)
    for i in range(constant.scanner_thread):
        scanner = Scanner()
        scanner.start()
        scannerWorkers.append(scanner)


def isStopped():
    return False


def getUsers():
    users = [constant.changhao]
    return users


def exportTransactions():
    with open("txns.log", 'a') as f:
        for t in transactionWorkers:
            for i in t.products:
                f.write(i.print())


def existProduct(product):
    for i in products:
        if i.id == product.id:
            return True
    return False


if __name__ == '__main__':
    try:
        start()
        while True:
            product = Scanner.products.get()
            if product is None:
                break
            if existProduct(product):
                continue
            products.append(product)
            for t in transactionWorkers:
                if t.is_waitting and t.user.rule(t, product):
                    t.transactionQueue.put(product)
        stop()
        log.flush()
        exportTransactions()
    except KeyboardInterrupt:
        stop()
        log.flush()
        exportTransactions()

    log.info("end...")
