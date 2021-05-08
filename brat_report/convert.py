
import os
import random
import json
import jieba
import itertools

def list_txt_ann(brat_raw_folder):
    files = os.listdir(brat_raw_folder)
    files = sorted(files)
    for file in files:
        if 'txt' in file:
            yield os.path.join(brat_raw_folder, file), os.path.join(brat_raw_folder, file.replace('txt', 'ann'))

def process_one_file_junk(txt, ann, only_mid=True):
    """
    把除ann中标注的具有供应关系的实体的实体对取出来，作为no_relation
    @param: only_mid: 是否只截取出中间部分
    @return:
    [
        {"tokens": ["SUBJCompany", "目前", "是", "OBJProduct", "领域", "最大", "的", "国产", "IGBT", "供应商", "，", "产品", "应用", "以", "A00", "车型", "为主", "，", "明年", "目标", "是", "毛利", "更", "高", "的", "A", "级车"], "subj_start": 0, "subj_end": 0, "obj_start": 3, "obj_end": 3, "relation": "produce_relation"},
        {"tokens": ["SUBJCompany", "与", "深南电", "路", "、", "生益", "电子", "、", "方正", "电路", "、", "景旺", "电子", "、", "沪", "电", "股份", "、", "OBJCompany", "等", "PCB", "龙头企业", "保持", "战略", "合作", "关系", "，", "有望", "受益", "5G", "发展", "带来", "的", "PCB", "板块", "的", "高", "景气", "发展"], "subj_start": 0, "subj_end": 0, "obj_start": 18, "obj_end": 18, "relation": "supply_relation"}
    ]
    relation: 'no_relation', 'produce_relation', 'supply_relation'
    SUBJCompany, OBJProduct, OBJCompany
    """
    with open(txt, 'r') as f:
        sentence = f.readline().strip()
    T = dict()
    R = []
    ans_sents = []
    with open(ann, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('T'):
                eles = line.split('\t')
                second = eles[1].split(' ')
                second[1] = int(second[1])
                second[2] = int(second[2])
                second.append(eles[2])
                T[eles[0]] = tuple(second) # T3: (产品,59,65,集成电路行业)
            elif line.startswith('R'):
                ele = line.split('\t')[1] # 生产 Arg1:T1 Arg2:T3
                eles = ele.split(' ')
                _type = eles[0]
                arg1 = eles[1][5:]
                arg2 = eles[2][5:]
                R.append((_type, arg1, arg2))
        supply_pairs = set()
        for r in R:
            _type, arg1, arg2 = r
            supply_pairs.add((arg1, arg2))
            supply_pairs.add((arg2, arg1))

        for arg1 in T:
            for arg2 in T:
                if arg1 == arg2:
                    continue
                if (arg1, arg2) in supply_pairs:
                    continue

                def to_tokens(_sentence, _subj, _obj, abort_entities=False):
                    _subj = ' ' + _subj + ' '
                    _obj = ' ' + _obj + ' '
                    t1, t2 = T[arg1], T[arg2]
                    if t1[2] < t2[1]:
                        _sentence = _sentence[:t2[1]] + _obj + _sentence[t2[2]:]
                        _sentence = _sentence[:t1[1]] + _subj + _sentence[t1[2]:]
                    else:
                        _sentence = _sentence[:t1[1]] + _subj + _sentence[t1[2]:]
                        _sentence = _sentence[:t2[1]] + _obj + _sentence[t2[2]:]
                    
                    # 把所有实体扔掉
                    if abort_entities:
                        for t in T:
                            _sentence = _sentence.replace(T[t][3], '')
                    _tokens = jieba.lcut(_sentence)
                    ans = [t.strip() for t in _tokens if t != ' ' and t != '  ']
                    return ans

                _type = '供应'
                subj = 'SUBJCompany'
                obj = 'OBJCompany'
                relation = 'no_relation'
                tokens = to_tokens(sentence, subj, obj, abort_entities=False)
                
                # 找到头 尾 实体的位置
                def find_pos(_tokens, _subj, _obj):
                    s, e = -1, -1
                    for idx, t in enumerate(tokens):
                        if t == subj:
                            s = idx
                        if t == obj:
                            e = idx
                    return s, e
                s, e = find_pos(tokens, subj, obj)
                data = {
                    'tokens': tokens,
                    "subj_start": s, 
                    "subj_end": s, 
                    "obj_start": e, 
                    "obj_end": e, 
                    "relation": relation
                }
                json_data = json.dumps(data, ensure_ascii=False)
                ans_sents.append(json_data)
                print(json_data)
    
    return ans_sents


def process_one_file(txt, ann, only_mid=True):
    """
    把ann中标注的两个实体拿出来
    @param: only_mid: 是否只截取出中间部分
    @return:
    [
        {"tokens": ["SUBJCompany", "目前", "是", "OBJProduct", "领域", "最大", "的", "国产", "IGBT", "供应商", "，", "产品", "应用", "以", "A00", "车型", "为主", "，", "明年", "目标", "是", "毛利", "更", "高", "的", "A", "级车"], "subj_start": 0, "subj_end": 0, "obj_start": 3, "obj_end": 3, "relation": "produce_relation"},
        {"tokens": ["SUBJCompany", "与", "深南电", "路", "、", "生益", "电子", "、", "方正", "电路", "、", "景旺", "电子", "、", "沪", "电", "股份", "、", "OBJCompany", "等", "PCB", "龙头企业", "保持", "战略", "合作", "关系", "，", "有望", "受益", "5G", "发展", "带来", "的", "PCB", "板块", "的", "高", "景气", "发展"], "subj_start": 0, "subj_end": 0, "obj_start": 18, "obj_end": 18, "relation": "supply_relation"}
    ]
    relation: 'no_relation', 'produce_relation', 'supply_relation'
    SUBJCompany, OBJProduct, OBJCompany
    """
    with open(txt, 'r') as f:
        sentence = f.readline().strip()
    T = dict()
    R = []
    ans_sents = []
    with open(ann, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('T'):
                eles = line.split('\t')
                second = eles[1].split(' ')
                second[1] = int(second[1])
                second[2] = int(second[2])
                second.append(eles[2])
                T[eles[0]] = tuple(second) # T3: (产品,59,65,集成电路行业)
            elif line.startswith('R'):
                ele = line.split('\t')[1] # 生产 Arg1:T1 Arg2:T3
                eles = ele.split(' ')
                _type = eles[0]
                arg1 = eles[1][5:]
                arg2 = eles[2][5:]
                R.append((_type, arg1, arg2))
        for r in R:
            _type, arg1, arg2 = r
            def to_tokens(_sentence, _subj, _obj, abort_entities=False):
                _subj = ' ' + _subj + ' '
                _obj = ' ' + _obj + ' '
                t1, t2 = T[arg1], T[arg2]
                if t1[2] < t2[1]:
                    _sentence = _sentence[:t2[1]] + _obj + _sentence[t2[2]:]
                    _sentence = _sentence[:t1[1]] + _subj + _sentence[t1[2]:]
                else:
                    _sentence = _sentence[:t1[1]] + _subj + _sentence[t1[2]:]
                    _sentence = _sentence[:t2[1]] + _obj + _sentence[t2[2]:]
                
                # 把所有实体扔掉
                if abort_entities:
                    for t in T:
                        _sentence = _sentence.replace(T[t][3], '')
                _tokens = jieba.lcut(_sentence)
                ans = [t.strip() for t in _tokens if t != ' ' and t != '  ']
                return ans

            if _type == '生产':
                subj = 'SUBJCompany'
                obj = 'OBJProduct'
                relation = 'produce_relation'
                tokens = to_tokens(sentence, subj, obj, abort_entities=False)
                
            elif _type == '供应':
                subj = 'SUBJCompany'
                obj = 'OBJCompany'
                relation = 'supply_relation'
                tokens = to_tokens(sentence, subj, obj, abort_entities=False)
            
            # 找到头 尾 实体的位置
            def find_pos(_tokens, _subj, _obj):
                s, e = -1, -1
                for idx, t in enumerate(tokens):
                    if t == subj:
                        s = idx
                    if t == obj:
                        e = idx
                return s, e
            s, e = find_pos(tokens, subj, obj)
            data = {
                'tokens': tokens,
                "subj_start": s, 
                "subj_end": s, 
                "obj_start": e, 
                "obj_end": e, 
                "relation": relation
            }
            json_data = json.dumps(data, ensure_ascii=False)
            ans_sents.append(json_data)
            print(json_data)
    
    return ans_sents

def process(brat_raw_folder, brat_output_folder):
    ans = []
    for txt, ann in list_txt_ann(brat_raw_folder):
        cur = process_one_file(txt, ann)
        if 'supply' in txt:
            cur += process_one_file_junk(txt, ann)
        ans += cur
    random.shuffle(ans)
    with open(os.path.join(brat_output_folder, 'mannual_lable_test.json'), 'w') as f:
        for i in ans:
            f.write(i)
            f.write('\n')

if __name__ == '__main__':
    brat_raw_folder = '/home/ps/disk_sdb/yyr/codes/NEROzh/data/brat_raw'
    brat_output_folder = '/home/ps/disk_sdb/yyr/codes/NEROzh/data/brat_data'
    process(brat_raw_folder, brat_output_folder)