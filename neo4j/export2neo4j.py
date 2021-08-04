import os
import json
from py2neo import Graph,Node,Relationship

def list_txt_ann(brat_raw_folder):
    files = os.listdir(brat_raw_folder)
    files = sorted(files)
    for file in files:
        if 'txt' in file:
            yield os.path.join(brat_raw_folder, file), os.path.join(brat_raw_folder, file.replace('txt', 'ann'))


def process_one_file(txt, ann):
    """
    把ann中标注的两个实体拿出来

    """
    with open(txt, 'r') as f:
        sentence = f.readline().strip()
    T = dict()
    R = []
    ans_triplets = []
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
        relation2type = {
            '供应产品': '产品',
            '供应': '企业',
            '合作': '企业'
            }
        for r in R:
            _type, arg1, arg2 = r
            triplet = [_type, T[arg1][3], T[arg2][3]]
            triplet.append('企业')
            triplet.append(relation2type[_type])

            ans_triplets.append(tuple(triplet)) # ('供应', '山东威达', '蔚来', '企业', '企业')
        return ans_triplets




def export2neo4j(ans):
    test_graph = Graph(
        "http://localhost:7474", 
        username="neo4j", 
        password="123456"
    )

    name2node = dict()
    
    for i in ans:
        print(i)
        relation, subj, obj, subj_type, obj_type = i

        if subj is None or obj is None:
            continue
        if subj not in name2node:
            name2node[subj] = Node(subj_type, name=subj)
            test_graph.create(name2node[subj])
        subj_node = name2node[subj]
        if obj not in name2node:
            name2node[obj] = Node(obj_type, name=obj)
            test_graph.create(name2node[obj])
        obj_node = name2node[obj]
        node_1_call_node_2 = Relationship(subj_node, relation, obj_node)
        test_graph.create(node_1_call_node_2)


def process(*folders):
    ans = []
    for folder in folders:
        for txt, ann in list_txt_ann(folder):
            cur = process_one_file(txt, ann)
            # print(cur)
            ans += cur
    print(len(ans))
    export2neo4j(ans)


if __name__ == '__main__':
    path1 = '/home/ps/disk_sdb/yyr/codes/NEROtorch/data/supply_cooperate_20210518_raw/supply'
    path2 = '/home/ps/disk_sdb/yyr/codes/NEROtorch/data/supply_cooperate_20210518_raw/cooperate'
    process(path1, path2)