from elasticsearch import Elasticsearch
import json
import threading

res=[]
class EasyES(object):

    def __init__(self, host, output):
        self.es = Elasticsearch(hosts=host)
        self.output = output

    def query_multi_thread(self, sql: str, index=""):
        for i in range(0,10):
            sql["slice"]={"id":i,"max":10}
            t=threading.Thread(target=self.search_by_sql,args=(sql,index,))
            t.run()
            self.search_by_sql(sql,index)



    def search_by_sql(self, sql: str, index=""):
        '''
        根据sql查询，并写入到文件，文件在
        :param output_name: 输出文件名
        :param index: 查询索引，若为空，则查询所有索引
        :param sql: 查询sql
        :return: 返回ip的list，已去重
        '''
        if index == '':
            query = self.es.search(body=sql, scroll='5m', size=100)
        else:
            query = self.es.search(index=index, body=sql, scroll='5m', size=100)

        results = query['hits']['hits']  # es查询出的结果第一页
        total = query['hits']['total']  # es查询出的结果总量
        print("total hits {}".format(total))
        scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
        for i in range(0, int(total / 100) + 1):
            # print(i * 100)
            # scroll参数必须指定否则会报错
            query_scroll = self.es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
            results += query_scroll
        global res
        res=res+results
        # 由于 banner_global_0817没有banner length字段，因此根据banner长度排序
        # results = sorted(results, key=lambda x: len(x['_source']['service'][0]['banner']), reverse=True)

        ip_li = [x['_source']['ip']+':'+
                 str(x['_source']['service'][0]['layer']['transport']['port'])
                 for x in results]
        #ip_li = [x['_source']['ip'] for x in results]
        # ip_set = set(ip_li)
        # ip_li = list(ip_set)

        if self.output == '':
            return ip_li

        with open(self.output, 'w') as f:
            json.dump(results, f)
        print(ip_li)
        return ip_li


if __name__ == '__main__':
    sql_jetlinks = {"query": {"bool": {"must": [{"match_phrase": {"service.banner": "connection code: 0"}},
                                                {"range": {"features.banner_length": {"gt": "2000"}}}]}},
                    "sort": {"features.banner_length": {"order": "desc"}}, "aggs": {}}
    es = EasyES('192.168.19.14','./result/global_1883.json')
    #ip = es.search_by_sql(sql_jetlinks, 'banner_global_1883_2021-07-05')
    ip=es.query_multi_thread(sql_jetlinks, 'banner_global_1883_2021-07-05')
    pass
