import random

from tqdm import tqdm
from collections import defaultdict

from dataset import read
from langcache.core import Cache


# Preprocessing.
id_to_question = {}
similarity_question = defaultdict(lambda: set([]))

total = 0
total_similar = 0

for data in read():
    total += 1
    qid1 = data["qid1"]
    qid2 = data["qid2"]
    q1 = data["q1"]
    q2 = data["q2"]
    duplicate = data["duplicate"]
    if qid1 not in id_to_question:
        id_to_question[qid1] = q1
    if qid2 not in id_to_question:
        id_to_question[qid2] = q2
    if duplicate:
        similarity_question[qid1].add(qid2)
        similarity_question[qid2].add(qid1)
        total_similar += 1

print("Total pair", total)
print("Total similar pair", total_similar)
print("Num of question", len(id_to_question))

qid_list = list(id_to_question.keys())
qid_list = qid_list[:200]
split_idx = len(qid_list) // 2

random.seed(0)
random.shuffle(qid_list)

train_qid_list, test_qid_list = set(qid_list[:split_idx]), set(qid_list[split_idx:])

cache = Cache(tune_frequency=0, tune_policy="recall")
for train_qid in tqdm(train_qid_list):
    # Insert cache.
    cache.put(id_to_question[train_qid], str(train_qid))

tp, fn, fp = 0, 0, 0
for i, test_qid in tqdm(enumerate(test_qid_list)):
    # Test tuning.
    if i % 5 == 0:
        ret_key, ret_value, ret_distance = cache._top_k(id_to_question[test_qid])
        response = "Equal" if int(ret_value) in similarity_question[test_qid] else "Not Equal"
        cache._evaluate_and_tune(id_to_question[test_qid], ret_key, ret_distance, response=response)

    # Get cache.
    train_qid = cache.get(id_to_question[test_qid])

    # Get evaluation metrics.
    if train_qid is not None:
        train_qid = int(train_qid)
        assert train_qid != test_qid
        if test_qid in similarity_question[train_qid]:
            tp += 1
        else:
            fp += 1
    else:
        similar_qid_list = similarity_question[test_qid]
        if len(similar_qid_list & train_qid_list) != 0:
            fn += 1

print("Precision", tp / (tp + fp))
print("Recall", tp / (tp + fn))
print("TP FN FP", tp, fn, fp)
