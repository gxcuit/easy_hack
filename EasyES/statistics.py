import json
import re
import geoip2.database

# 流程：
#   1.es中根据sql（banner）进行查询
#   2. 去重（set实现），ip和port
#   3. 统计国家、版本



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

def country_stastics(ip_list):
    '''
    国家统计
    Args:
        ip_list: ip列表
        country: 国家名，默认为空，如果提供，则仅输出该国家的数据

    Returns: 国家的dict，key是国家英文名，value是数量

    '''
    country_dict = {}
    with geoip2.database.Reader('./GeoLite2-Country.mmdb') as reader:
        for ip in ip_list:
            resp=reader.country(ip)
            country = resp.country.names.get('en','No country')
            country_dict[country]=1+country_dict.setdefault(country,0)
    return sorted(country_dict.items(),key=lambda x:x[1],reverse=True)

def get_ip_by_country(ip_li:list,country:str):
    '''
    根据国家返回ip
    Args:
        ip_li:
        country:

    Returns:

    '''
    res=[]
    with geoip2.database.Reader('./GeoLite2-Country.mmdb') as reader:
        for ip in ip_li:
            resp = reader.country(ip)
            if country.lower()==resp.country.names.get('en', 'No country').lower():
                res.append(ip)
    return res

def unauthorized_country_stastics(file):
    with open(file,'r') as f:
        j = json.load(f)
        total=0
        country_dicy = {}
        for i in j:
            banner=i['_source']['service'][0]['banner']
            if 'MQTT Connection Code: 0' not in banner:
                continue
            ip=i['_source']['ip']
            total+=1
            with geoip2.database.Reader('./GeoLite2-Country.mmdb') as reader:
                resp=reader.country(ip)
                country = resp.country.names.get('en','No country')
                country_dicy[country]=1+country_dicy.setdefault(country,0)
    print(sorted(country_dicy.items(),key=lambda x:x[1],reverse=True))
    pass

def ip_port_deduplication(file):
    '''
    对查询的数据文件，ip、端口去重
    Args:
        file:

    Returns:

    '''
    with open(file,'r') as f:
        j = json.load(f)
        ip_set=set()
        for i in j:
            data=i['_source']['ip'] + ':' + str(i['_source']['service'][0]['layer']['transport']['port'])
            ip_set.add(data)
    return list(ip_set)

if __name__ == '__main__':
    #unauthorized_country_stastics('./result/version-07-05-global.json')
    #dedup_res=ip_port_deduplication('./result/thingsboard.json')

    with open('../EasyBF/success.json','r') as f:
        dedup_res=json.load(f)
        dedup_res=[x[0].split(':')[0] for x in dedup_res]
        print(country_stastics(dedup_res))

