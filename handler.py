import urllib3

import constant
import log
from scanner import Scanner
from transaction import Transaction

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

scannerWorkers = []
transactionWorker = None
products = []


# 结束所有线程
def stop():
    for scanner in scannerWorkers:
        scanner.stop()
        scanner.join()
    transactionWorker.transactionQueue.put(None)
    transactionWorker.join()
    log.flush()
    exportTransactions()


# 启动扫描和交易线程
def start():
    log.info("start...")
    global transactionWorker
    transactionWorker = Transaction(get_user())
    transactionWorker.login()
    transactionWorker.start()
    for i in range(constant.scanner_thread):
        scanner = Scanner()
        scanner.start()
        scannerWorkers.append(scanner)


def get_user():
    return constant.changhao


def exportTransactions():
    with open("txns.log", 'a') as f:
        for i in transactionWorker.products:
            f.write(i.print())


def get_best(ps):
    ps.sort(key=lambda p: p.amount, reverse=True)
    for p in ps:
        if product.id in products:
            continue
        products[p.id] = p
        if p.status == product.STATUS_TRANSACTIONFAILED:
            continue
        if transactionWorker.user.rule(transactionWorker, p):
            return p


if __name__ == '__main__':
    try:
        start()
        while True:
            product_ary = Scanner.products.get()
            if product_ary is None:
                break
            if transactionWorker.hasBought():
                break
            if transactionWorker.is_waitting:
                continue
            product = get_best(product_ary)
            if product:
                log.debug(product.print_self())
                transactionWorker.transactionQueue.put(product)
        stop()
    except KeyboardInterrupt:
        stop()

    log.info("end...")
