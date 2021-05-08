(tf1.10) ps@ps:~/disk_sdb/yyr/codes/NERO$ python semeval.py 
train patterns
972 labeled data
Epoch: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 50/50 [04:55<00:00,  5.91s/it]
acc: 0.6675461741424802, rec: 0.5622222222222222, f1: 0.6103739445114595



## 在report研报上
(tf1.10) ps@ps:~/disk_sdb/yyr/codes/NEROzh$ python semeval.py
load word embedding...
100%|████████████████████████████████| 678718/678718 [00:23<00:00, 28511.80it/s]
load word embedding done.
train patterns
2283 labeled data
Epoch: 100%|████████████████████████████████████| 50/50 [42:02<00:00, 50.45s/it]
acc: 0.9985, rec: 0.9985, f1: 0.9985


load word embedding...
100%|██████████████████████████████████| 52214/52214 [00:01<00:00, 32776.47it/s]
load word embedding done.
train patterns
1682 labeled data
Epoch: 100%|████████████████████████████████████| 50/50 [16:22<00:00, 19.64s/it]
acc: 0.9970089730807578, rec: 0.9852216748768473, f1: 0.9910802775024777


(tf1.10) ps@ps:~/disk_sdb/yyr/codes/NEROzh$ python semeval.py
load word embedding...
100%|██████████████████████████████████| 52214/52214 [00:01<00:00, 31210.33it/s]
load word embedding done.
train patterns
180 labeled data
Epoch: 100%|██████████████████████████████████████| 2/2 [00:10<00:00,  5.37s/it]
acc: 0.8801169590643275, rec: 0.8157181571815718, f1: 0.8466947960618847



## 在手标的数据集上测试
(tf1.10) ps@ps:~/disk_sdb/yyr/codes/NEROzh$ python semeval.py 
load word embedding...
100%|████████████████████████████████████████████████████████████████████████████████████████████| 52214/52214 [00:01<00:00, 29740.28it/s]
load word embedding done.
train patterns
180 labeled data
Epoch: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:08<00:00,  4.27s/it]
acc: 0.7540777917189461, rec: 0.8536931818181818, f1: 0.8007994670219855

## 在手标的数据集上测试，负样本使用无关系的pairs，所以正样本大概600多条，负样本8000条
load word embedding...
100%|████████████████████████████████████████████████████████████████████████████████████████████| 52214/52214 [00:01<00:00, 29734.61it/s]
load word embedding done.
train patterns
180 labeled data
Epoch: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:41<00:00, 20.89s/it]
acc: 0.9923857868020305, rec: 0.5507042253521127, f1: 0.7083333333333334

CUDA_VISIBLE_DEVICES=2 python semeval.py

curl -H "Content-Type:application/json" -H "Data_Type:msg" -X POST --data '{"sentences": ["SUBJCompany目前是OBJProduct领域最大的国产IGBT供应商", "SUBJCompany目前是OBJProduct领域最大的国产IGBT供应商"]}' http://127.0.0.1:20003/process
