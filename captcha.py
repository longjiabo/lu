import base64

import requests

import constant


class Captcha:
    session = requests.session()

    def __init__(self, captchaBytes, imageId):
        self.result = None
        self.imageId = imageId
        self.session.verify = False
        self.content = captchaBytes

    def requestCaptcha(self):
        data = constant.captcha
        data['file_base64'] = base64.b64encode(self.content)
        res = self.session.post("http://upload.chaojiying.net/Upload/Processing.php",
                                data=data)
        o = res.json()
        self.result = o['pic_str']
        return self
