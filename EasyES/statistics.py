import json
import re
import geoip2.database

def version_statistics(file):
    version_dict={}
    version_dict['no version']=0
    total=0
    with open(file,'r') as f:
        j=json.load(f)
        for i in j:
            banner=i['_source']['service'][0]['banner']
            res=re.findall('version:(.+)',banner)
            total += 1
            if res:
                for i in res:
                #print(res[0])
                    version_dict[i]=version_dict.setdefault(i,0)+1

            else:
                version_dict['no version']+=1
    print(total)
    print(sorted(version_dict.items(),key=lambda x:x[1],reverse=True))

def country_stastics(file):
    with open(file,'r') as f:
        j = json.load(f)
        total=0
        country_dicy = {}
        for i in j:
            ip=i['_source']['ip']
            total+=1
            with geoip2.database.Reader('./GeoLite2-Country.mmdb') as reader:
                resp=reader.country(ip)
                country = resp.country.names.get('en','No country')
                country_dicy[country]=1+country_dicy.setdefault(country,0)
    print(sorted(country_dicy.items(),key=lambda x:x[1],reverse=True))
    pass

if __name__ == '__main__':
    country_stastics('./result/version-07-05-global.json')