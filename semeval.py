from __future__ import unicode_literals
import os
import tensorflow as tf
import semeval_constant as constant
import json
import random
import numpy as np
import jieba

from main import train, read, predict


from flask import Flask, flash, request

app = Flask(__name__)


flags = tf.flags
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

flags.DEFINE_string("dataset", "semeval", "")
flags.DEFINE_string("mode", "regd", "pretrain / pseudo / regd")
flags.DEFINE_string("gpu", "3", "The GPU to run on")


flags.DEFINE_string("pattern_file", "./data/report/yanbao_ic_pattern.json", "")
flags.DEFINE_string("target_dir", "data", "")
flags.DEFINE_string("log_dir", "log/event", "")
flags.DEFINE_string("save_dir", "log/model", "")
flags.DEFINE_string("glove_word_file", "./data/glove/glove.840B.300d.txt", "")

# flags.DEFINE_string("train_file", "./data/report/train.json", "")
# flags.DEFINE_string("dev_file", "./data/report/dev.json", "")
# flags.DEFINE_string("test_file", "./data/report/test.json", "")

flags.DEFINE_string("train_file", "./data/report/train.json", "")
flags.DEFINE_string("dev_file", "./data/brat_data/mannual_lable_test.json", "")
flags.DEFINE_string("test_file", "./data/brat_data/mannual_lable_test.json", "")

flags.DEFINE_string("emb_dict", "./data/report/emb_dict.json", "")

flags.DEFINE_string("checkpoint", "./checkpoint/model.ckpt", "")
# 是否训练或测试
flags.DEFINE_string("train_mode", "predict", "train or predict")

flags.DEFINE_integer("glove_word_size", int(2.2e6), "Corpus size for Glove")
flags.DEFINE_integer("glove_dim", 300, "Embedding dimension for Glove")
flags.DEFINE_integer("top_k", 100000, "Finetune top k words in embedding")
flags.DEFINE_integer("length", 110, "Limit length for sentence")
flags.DEFINE_integer("num_class", len(constant.LABEL_TO_ID), "Number of classes")
flags.DEFINE_string("tag", "", "The tag name of event files")

flags.DEFINE_integer("batch_size", 8, "Batch size")
flags.DEFINE_integer("pseudo_size", 8, "Batch size for pseudo labeling")
flags.DEFINE_integer("num_epoch", 4, "Number of epochs")
flags.DEFINE_float("init_lr", 0.5, "Initial lr")
flags.DEFINE_float("lr_decay", 0.95, "Decay rate")
flags.DEFINE_float("keep_prob", 0.5, "Keep prob in dropout")
flags.DEFINE_float("grad_clip", 5.0, "Global Norm gradient clipping rate")
flags.DEFINE_integer("hidden", 200, "Hidden size")
flags.DEFINE_integer("att_hidden", 200, "Hidden size for attention")

flags.DEFINE_float("alpha", 0.1, "Weight of pattern RE")
flags.DEFINE_float("beta", 0.2, "Weight of similarity score")
flags.DEFINE_float("gamma", 0.5, "Weight of pseudo label")
flags.DEFINE_float("tau", 0.7, "Weight of tau")
flags.DEFINE_list("patterns", [], "pattern list")


g_config = None
g_test_data = None
g_patterns = None
g_word2idx_dict = None
g_match = None
g_sess = None
g_best_entro = None

def seed_tensorflow(seed=42):
    
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    tf.set_random_seed(seed)

def main(_):
    config = flags.FLAGS
    os.environ["CUDA_VISIBLE_DEVICES"] = config.gpu

    with open(config.pattern_file, "r") as fh:
        patterns = json.load(fh)
    config.patterns = patterns
    data = read(config)
    if config.train_mode == 'predict':
        config, test_data, patterns, word2idx_dict, match, sess, best_entro = train(config, data)

        global g_config
        global g_test_data
        global g_patterns
        global g_word2idx_dict
        global g_match
        global g_sess
        global g_best_entro

        g_config, g_test_data, g_patterns, g_word2idx_dict, g_match, g_sess, g_best_entro = \
            config, test_data, patterns, word2idx_dict, match, sess, best_entro

        print('wait for sentences to input')
        # res = []
        # with open(config.test_file, "r") as fh:
        #     for line in fh:
        #         line = line.strip()
        #         if len(line) > 0:
        #             res.append(line)
        

        # predict(g_config, res, g_patterns, g_word2idx_dict, g_match, g_sess, 'test', entropy=g_best_entro)
    else:
        train(config, data)
    




def convert(sentence):
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
        'relation': 'no_relation'
    }
    json_data = json.dumps(json_data, ensure_ascii=False)
    return json_data


@app.route('/')
def home():
    return '<h1>hello world</h1>'

@app.route('/process', methods=['POST'])
def process():
    global g_config
    global g_test_data
    global g_patterns
    global g_word2idx_dict
    global g_match
    global g_sess
    global g_best_entro
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data)['sentences']
        sentences = [convert(d) for d in data]
        
        ans = predict(g_config, sentences, g_patterns, g_word2idx_dict, g_match, g_sess, 'test', entropy=g_best_entro)
        return json.dumps({'code': 200, 'msg': ans}, ensure_ascii=False)
    else:
        return json.dumps({'code': -1, 'msg': 'please use post.'}, ensure_ascii=False)

main(_='')

if __name__ == "__main__":
    seed_tensorflow()
    # tf.app.run()
    app.run(debug=True, host='0.0.0.0', port=20003)
