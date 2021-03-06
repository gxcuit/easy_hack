from elasticsearch import Elasticsearch
import json
import threading
import time
import multiprocessing

es=Elasticsearch(hosts='192.168.19.14')



def seqrch(index,sql,res=[]):
    if index=='':
        query = es.search(body=sql, scroll='5m', size=1000)
    else:
        query = es.search(index=index, body=sql, scroll='5m', size=1000)
    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    print("total hits {}".format(total))
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    for i in range(0, int(total / 1000) + 1):
        # print(i * 100)
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
        results += query_scroll
    # 由于 banner_global_0817没有banner length字段，因此根据banner长度排序
    # results = sorted(results, key=lambda x: len(x['_source']['service'][0]['banner']), reverse=True)
    es.clear_scroll(scroll_id=scroll_id)
    ip_li = [x['_source']['ip'] + ':' +
             str(x['_source']['service'][0]['layer']['transport']['port'])
             for x in results]


    # with open(output, 'w') as f:
    #     json.dump(results, f)
    #print(ip_li)
    #global res
    #res.append(results)
    res+=results
    #print(len(res))
    return results

def mul_process_search(sql,process_number,index=''):
    process=[]
    #pool = multiprocessing.Pool(processes=3)
    res_list=multiprocessing.Manager().list()
    for i in range(process_number):
        sql["slice"]={"id":i,"max":process_number}
        #pool.apply_async(seqrch,args=(index,sql,res_list,))
        p=multiprocessing.Process(target=seqrch,args=(index,sql,res_list,))
        process.append(p)
        p.start()
    for i in process:
        i.join()
    #pool.close()
    #pool.join()
    # global res
    #print(type(res_list))
    return list(res_list)

if __name__ == '__main__':
    sql = {"query": {"bool": {"must": [{"match_phrase": {"service.banner": "connection code: "}},
                                                {"range": {"features.banner_length": {"gt": "2000"}}}]}},
                    "sort": {"features.banner_length": {"order": "desc"}}, "aggs": {}}
    start = time.time()
    #seqrch(index='banner_global_1883_2021-07-05',sql=sql,res=res)

    # 版本统计
    sql_verison={"query":{"bool":{"must":[{"match_phrase":{"service.banner":"connection code: "}}
                                                                   ]}},"aggs":{}}

    sql_thingsboard={"query":{"bool":{"must":[{"match_phrase":{"service.banner":"Thingsboard Authors"}}]}},"aggs":{}}


    res=mul_process_search(sql=sql_thingsboard,process_number=3)
    #res=seqrch(index='banner_cn_1883_2021-07-30',sql=sql_verison)
    #print(len(res))
    end=time.time()
    print("total {}---\n used time {}".format(len(res),end-start))
    with open('./result/thingsboard.json','w') as f:
        json.dump(res,f)
    pass
