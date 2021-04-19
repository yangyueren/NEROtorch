## 基于英文NERO，改造为中文的

需要先用semeval_preprocess.py将数据处理为
{"tokens": ["The", "most", "common", "SUBJ-O", "were", "about", "OBJ-O", "and", "recycling"], "subj_start": 3, "subj_end": 3, "obj_start": 6, "obj_end": 6, "relation": "Message-Topic(e1,e2)"}
格式
pattern.json格式：
[["Cause-Effect(e1,e2)", "SUBJ-O caused a OBJ-O"], ["Cause-Effect(e1,e2)", "SUBJ-O cause OBJ-O"]]

在semeval_loader.py/read_glove中加载中文word embedding
