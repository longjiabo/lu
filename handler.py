import urllib3
from scanner import Scanner
from transaction import Transaction

import log, constant

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
            if product.status == product.STATUS_TRANSACTIONFAILED:
                continue
            log.debug(product.print_self())
            if transactionWorker.hasBought():
                break
            if transactionWorker.is_waitting and transactionWorker.user.rule(transactionWorker, product):
                transactionWorker.transactionQueue.put(product)
        stop()
        log.flush()
        exportTransactions()
    except KeyboardInterrupt:
        stop()
        log.flush()
        exportTransactions()

    log.info("end...")
