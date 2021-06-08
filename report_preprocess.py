#!/usr/bin/python3

import re
import json
import jieba
import random
import re
import os
import json
import shutil
import itertools
"""
从ner识别好的文本中，用规则抽取出关系
"""

##################################
company_product_pattern = {
        "produce_words": [
            "公司是.+供应商",
            "公司是.+商",
            "公司是.+企业",
            "是.+公司",
            "是.+企业",
            "生产.+材料",
            "从事.*[研发|生产|销售]",
            "致力于.*[研发|生产]",
            "公司.*龙头",
            "公司.*领先",
            "供应.*产品",
            "主要产品",
            "主营产品",
            "主营业务",
            "产品包括",
            "提供.*产品",
            "核心产品是",
        ],
        "supply_words": [
            "(.+)提供.+订单(.+)",
            "(.+)供货协议(.+)",
            "(.+)[切入|打入].*供应链(.+)",
            "(.+)新增.*客户(.+)",
            "(.+)客户包括(.+)",
            "(.+)主要客户(.+)",
            "(.+)与(.+)合作",
            "(.+)合作伙伴(.+)",
        ],
        "not_words": [
            "[0-9A-Za-z]{6,100}",
            "[0-9]{4,100}",
            "投资[、，]",
            "[0-9]+%",
            "具备.*投资.*资格",
            "电话",
            "证券研究报告",
            "《.+》",
            "是.+,.+公司"
            "是.+。.+公司",
            "联系我们",
            "地址"
        ]
}



def rename_company(data):
    # d = """
    # {"_id": "600a33a82514978c7c6f6c8b", "content": "考虑到公司为国内电动车龙头，新东方公司新技术新车型开启新周期，京东公司给予21年70倍PE，目标价105元，维持买入”评级", "companies": ["新东方公司", "京东公司"], "products": ["电动车"], "type": "company_product", "stockName": "比亚迪"}
    # """
    # data = json.loads(d)
    c = data['content']
    mask2com = {}
    for com in data['companies']:
        idx = c.find(com)
        # record company position
        mask2com[(idx, idx+len(com))] = com

    parts = []
    last_pos = 0
    while True:
        idx = c.find('公司')
        c = c.replace('公司', '岣岤', 1)
        if idx < 0:
            break
        flag = True
        for k in mask2com.keys():
            if idx >= k[0] and idx < k[1]:
                flag = False
        if flag:
            part = c[last_pos:idx]
            parts.append(part.replace('岣岤', '公司'))
            last_pos = idx + 2
    parts.append(c[last_pos:].replace('岣岤', '公司'))

    ans_content = data['stockName'].join(parts)
    data['rename_content'] = ans_content
    if data['stockName'] not in data['companies']:
        data['companies'].append(data['stockName'])
    return data


def extract_produce_from_sentence(data, words):
    ans = []
    if data['stockName'] not in data['rename_content']:
        return ans
    for c, p in itertools.product([data['stockName']], data['products']):
        if len(c) > 1 and len(p) > 1 and p in data['rename_content']:
            ans.append((c, p))
    return ans

def extract_supply_from_sentence(data, words):
    ans = []
    supply_words = company_product_pattern[words]
    sentence = data['rename_content']
    stock_name = data['stockName']
    for keyword in supply_words:
        res = re.search(keyword, sentence)
        if res is None:
            continue
        if stock_name not in sentence:
            continue
        com1_s, com2_s = res.groups()
        left, right = [], []
        for com in data['companies']:
            if stock_name == com or len(com) < 2:
                continue
            if com in com1_s:
                ans.append((stock_name, com))
            if com in com2_s:
                ans.append((stock_name, com))
    return ans
        

def check_regex(sentence, words):
    supply_words = company_product_pattern[words]
    for keyword in supply_words:
        if re.search(keyword, sentence):
            return True
    return False

def extract(ori_path, output, type_='company_product', words='produce_words'):
    with open(ori_path, 'r') as f:
        g = open(output, 'w')
        for line in f.readlines():
            try:
                data = json.loads(line)
                data = rename_company(data)
                
                if data['type'] == type_:
                    if not check_regex(data['rename_content'], words):
                        continue

                    else:
                        if type_ == 'company_product':
                            ans = extract_produce_from_sentence(data, words)
                            for pair in ans:
                                sentence = data['rename_content']
                                sentence = sentence.replace(pair[0], ' SUBJCompany ')
                                sentence = sentence.replace(pair[1], ' OBJProduct ')
                                tokens = jieba.lcut(sentence)
                                tokens = [t for t in tokens if t != '' and t != ' ']
                                ss, se = -1, -1
                                os, oe = -1, -1
                                for idx in range(len(tokens)):
                                    if tokens[idx] == 'SUBJCompany':
                                        ss = idx
                                        se = idx
                                    if tokens[idx] == 'OBJProduct':
                                        os = idx
                                        oe = idx
                                assert ss >= 0 and se >= 0, 'error'
                                assert os >= 0 and oe >= 0, 'error'
                                json_data = {
                                    'tokens': tokens,
                                    'subj_start': ss,
                                    'subj_end': se,
                                    'obj_start': os,
                                    'obj_end': oe,
                                    'relation': 'produce_relation'
                                }
                                json_data = json.dumps(json_data, ensure_ascii=False)
                                g.write(json_data)
                                g.write('\n')

                        elif type_ == 'company_company':
                            ans = extract_supply_from_sentence(data, words)
                            for pair in ans:
                                sentence = data['rename_content']
                                sentence = sentence.replace(pair[0], ' SUBJCompany ')
                                sentence = sentence.replace(pair[1], ' OBJCompany ')
                                tokens = jieba.lcut(sentence)
                                tokens = [t for t in tokens if t != '' and t != ' ']
                                ss, se = -1, -1
                                os, oe = -1, -1
                                for idx in range(len(tokens)):
                                    if tokens[idx] == 'SUBJCompany':
                                        ss = idx
                                        se = idx
                                    if tokens[idx] == 'OBJCompany':
                                        os = idx
                                        oe = idx
                                assert ss >= 0 and se >= 0, 'error'
                                assert os >= 0 and oe >= 0, 'error'
                                json_data = {
                                    'tokens': tokens,
                                    'subj_start': ss,
                                    'subj_end': se,
                                    'obj_start': os,
                                    'obj_end': oe,
                                    'relation': 'supply_relation'
                                }
                                json_data = json.dumps(json_data, ensure_ascii=False)
                                g.write(json_data)
                                g.write('\n')
            except Exception as e:
                print(e)
                
        g.close()

def get_pattern(datas, pattern_path):
    
    patterns = []
    num = 0
    for line in datas:
        data = json.loads(line)
        subj_start = data['subj_start']
        obj_start = data['obj_start']
        maxi = max(subj_start, obj_start)
        mini = min(subj_start, obj_start)
        tokens = data['tokens'][mini: maxi+1]
        pattern = " ".join(tokens)
        if len(pattern) < 200 and random.random() > 0.9:
            patterns.append([data['relation'],pattern])
            num += 1
    with open(pattern_path, 'w') as g:
        json_data = json.dumps(patterns, ensure_ascii=False)
        g.write(json_data)
        g.write('\n')
    print('Generate %d patterns.' % num)


def no_relation(ori_path, output):
    with open(ori_path, 'r') as f:
        g = open(output, 'w')
        for line in f.readlines():
            # try:
            data = json.loads(line)
            data = rename_company(data)
            if check_regex(data['rename_content'], 'produce_words') or check_regex(data['rename_content'], 'supply_words'):
                continue
            sentence = data['rename_content']
            if random.random() < 0.3:
                sentence = ' SUBJCompany ' + sentence
                sentence = sentence + ' OBJProduct '
                tokens = jieba.lcut(sentence)
                tokens = [t for t in tokens if t != '' and t != ' ']
            elif random.random() > 0.7:
                sentence = ' SUBJCompany ' + sentence
                sentence = sentence + ' OBJCompany '
                tokens = jieba.lcut(sentence)[:110]
                tokens = [t for t in tokens if t != '' and t != ' ']
            else:
                continue
            ss, se = 0, 0
            os, oe = len(sentence)-1, len(sentence)-1
            json_data = {
                'tokens': tokens,
                'subj_start': ss,
                'subj_end': se,
                'obj_start': os,
                'obj_end': oe,
                'relation': 'no_relation'
            }
            json_data = json.dumps(json_data, ensure_ascii=False)
            g.write(json_data)
            g.write('\n')
            # except Exception as e:
            #     print(e)
        g.close()


if __name__ == '__main__':

    input_path = './data/report/key_sentence_yanbao_prelabel_type.json'
    output_path = './data/report/yanbao_ic_produce_relation.json'
    output_path2 = './data/report/yanbao_ic_supply_relation.json'
    output_path3 = './data/report/yanbao_ic_no_relation.json'
    merge_path = './data/report/yanbao_ic_relation.json'
    pattern_path = './data/report/yanbao_ic_pattern.json'
    train_path = './data/report/train.json'
    dev_path = './data/report/dev.json'
    test_path = './data/report/test.json'
    # extract(input_path, output_path, type_='company_product', words='produce_words')
    # extract(input_path, output_path2, type_='company_company', words='supply_words')
    # no_relation(input_path, output_path3)
    datas = []
    def read(path, num=1000000000):
        f1 = open(path, 'r')
        idx = 0
        for line in f1:
            datas.append(line.strip())
            idx += 1
            if idx > num:
                break
        f1.close()
    read(output_path)
    read(output_path2)
    read(output_path3, num=2000)

    random.shuffle(datas)
    train = open(train_path, 'w')
    dev = open(dev_path, 'w')
    test = open(test_path, 'w')
    train_datas = []
    for line in datas:
        t = random.random()
        if t < 0.7:
            train.write(line)
            train_datas.append(line)
            train.write('\n')
        elif t > 0.9:
            dev.write(line)
            dev.write('\n')
        else:
            test.write(line)
            test.write('\n')
    get_pattern(train_datas, pattern_path)
    