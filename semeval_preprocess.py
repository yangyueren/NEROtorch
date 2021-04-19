#!/bin/python3

import re
import json

trainFile = './data/SemEval2010_task8_all_data/SemEval2010_task8_training/TRAIN_FILE.TXT'
testFile = './data/SemEval2010_task8_all_data/SemEval2010_task8_testing_keys/TEST_FILE_FULL.TXT'


op_trainFile = "./data/semeval/train.json"
op_testFile = "./data/semeval/test.json"


def createFile(filepath, outputpath):    
    
    fOut = open(outputpath, 'w')
    lines = [line.strip() for line in open(filepath)]
    for idx in range(0, len(lines), 4):
        sentence_num = lines[idx].split("\t")[0]
        sentence = lines[idx].split("\t")[1][1:-1]
        label = lines[idx+1].strip()
        if label == 'Other':
            label = 'no_relation'
        
        sentence = sentence.replace('.', ' ')

        subjo = r'<e1>.+</e1>'
        objo = r'<e2>.+</e2>'
        if label[-2] == '1':
            subjo, objo = objo, subjo
        sentence = re.sub(subjo, ' SUBJ-O ', sentence)
        sentence = re.sub(objo, ' OBJ-O ', sentence)
        print(sentence)
        tokens = sentence.split(' ')
        tokens = [t for t in tokens if t != '']
        ss, se = -1, -1
        os, oe = -1, -1
        for idx in range(len(tokens)):
            if tokens[idx] == 'SUBJ-O':
                ss = idx
                se = idx
            if tokens[idx] == 'OBJ-O':
                os = idx
                oe = idx
        assert ss >= 0 and se >= 0, 'error'
        assert os >= 0 and oe >= 0, 'error'
        data = {
            'tokens': tokens,
            'subj_start': ss,
            'subj_end': se,
            'obj_start': os,
            'obj_end': oe,
            'relation': label
        }
        json_data = json.dumps(data, ensure_ascii=False)
        fOut.write(json_data)
        fOut.write("\n")
    fOut.close()
        
    print(outputpath, "created")

if __name__ == '__main__':
    createFile(trainFile, op_trainFile)
    createFile(testFile, op_testFile)