from scipy import spatial
import numpy as np
from resources import SIF_embedding

from resources.InferSent import models
import torch
import sys
import re

# HYPER-PARAMETERS
INFERSENT_VERSION = 1
DATASET = 'basic-tasks'
USE_WEIGHTING = True
NUM_MATCHES = 1
######################

if len(sys.argv) >= 4:
    INFERSENT_VERSION = int(sys.argv[1])
    DATASET = sys.argv[2]
    USE_WEIGHTING = bool(sys.argv[3])

print('Running with the following parameters:')
print(f'InferSent: v{INFERSENT_VERSION}')
print(f'Data Set: {DATASET}')
print(f'Weighting: {USE_WEIGHTING}')

W2V_VERSION = 'fasttext' if INFERSENT_VERSION == 2 else 'glove'
V = INFERSENT_VERSION
MODEL_PATH = 'resources/encoder/infersent%s.pkl' % V
params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
infersent = models.InferSent(params_model)
infersent.load_state_dict(torch.load(MODEL_PATH))

W2V_PATH_FASTTEXT = '/home/berkeley/apps/pretrained_word_embeddings/crawl-300d-2M.vec'
W2V_PATH_GLOVE = '/home/berkeley/apps/pretrained_word_embeddings/glove.840B.300d.txt'

if W2V_VERSION == 'fasttext':
    infersent.set_w2v_path(W2V_PATH_FASTTEXT)
else:
    infersent.set_w2v_path(W2V_PATH_GLOVE)

infersent.build_vocab_k_words(K=300000)

TEST_CASE_FILE = f'data/test_cases/{DATASET}.csv'
GUIDANCE_EXAMPLES_FILE = f'data/guidance_data/{DATASET}.csv'

objects = []
verbs = []
actions = []


weighted_distance_measure_methods = [
    spatial.distance.cosine,
    spatial.distance.braycurtis,
    spatial.distance.canberra,
    spatial.distance.chebyshev,
    spatial.distance.cityblock,
    spatial.distance.correlation,
    spatial.distance.euclidean,
]


def get_test_cases(file_name):
    tcs = []
    with open(file_name) as tc_file:
        raw_tests = tc_file.readlines()
    for raw_test in raw_tests:
        v, o, text = raw_test.split(',')
        if v not in verbs:
            verbs.append(v)
        if o not in objects:
            objects.append(o)
        if v + ',' + o.strip() not in actions:
            actions.append(v + ',' + o.strip())
        tcs.append({'verb': v, 'obj': o, 'text': re.sub('\'', ' \' ', text).lower()})
    return tcs


def get_guidance_data(file_name):
    guiding_utterances = []
    guiding_verbs = []
    guiding_objects = []
    with open(file_name) as gd_file:
        examples = gd_file.readlines()
    for example in examples:
        v, o, text = example.split(',')
        guiding_verbs.append(v)
        guiding_objects.append(o)
        guiding_utterances.append(re.sub('\'', ' \' ', text).lower())
    return guiding_utterances, guiding_verbs, guiding_objects


def zero_vector():
    return np.zeros(4096)  # 4096 is the dimensionality of an infersent sentence embedding.


def get_weights():
    if not USE_WEIGHTING:
        return [1 / 4096] * 4096
    with open(f'resources/weights.csv', 'r') as weight_file:
        lines = weight_file.readlines()
    if DATASET in ['cod', 'handwritten', 'warcraft', 'generated']:
        dataset_key = DATASET
    else:
        dataset_key = 'cod'  # Use COD weights for all new datasets, it should be the most general
    for line in lines:
        split_line = line.split(',')
        if dataset_key not in split_line[0]:
            continue
        if str(INFERSENT_VERSION) not in split_line[1]:
            continue
        return [float(x) for x in split_line[2:-1]]
    raise NotImplementedError(f'No weights available for dataset: {DATASET}, infersent version: {INFERSENT_VERSION}')


weights = get_weights()


test_cases = get_test_cases(TEST_CASE_FILE)

object_vectors = infersent.encode(objects)
verb_vectors = infersent.encode(verbs)
action_vectors = infersent.encode([a.replace(',', ' ') for a in actions])

canonical_utterances, canonical_verbs, canonical_objects = get_guidance_data(GUIDANCE_EXAMPLES_FILE)

canonical_sets = list(zip(canonical_utterances, canonical_verbs, canonical_objects))

canonical_utterance_vectors_per_verb = {}
canonical_utterance_vectors_per_object = {}

verb_pcs = []
object_pcs = []

for verb in verbs:
    example_set = [u for u, v, o in canonical_sets if v == verb]
    canonical_utterance_vectors_per_verb[verb] = infersent.encode(example_set) if len(example_set) > 0 else [[]]
    verb_pcs.append(SIF_embedding.compute_pc(canonical_utterance_vectors_per_verb[verb]))

for obj in objects:
    example_set = [u for u, v, o in canonical_sets if o == obj]
    canonical_utterance_vectors_per_object[obj] = infersent.encode(example_set) if len(example_set) > 0 else [[]]
    object_pcs.append(SIF_embedding.compute_pc(canonical_utterance_vectors_per_object[obj]))

canonical_utterance_vectors = infersent.encode(canonical_utterances)
canonical_verb_vectors = infersent.encode(canonical_verbs)
canonical_object_vectors = []
for o in canonical_objects:
    if o:
        canonical_object_vectors.append(infersent.encode([o])[0])
    else:
        canonical_object_vectors.append([0] * 4096)
canonical_object_vectors = np.array(canonical_object_vectors)

verb_guidance_vector = zero_vector()
object_guidance_vector = zero_vector()
for i in range(len(canonical_utterance_vectors)):
    verb_guidance_vector += canonical_verb_vectors[i] - canonical_utterance_vectors[i]
    object_guidance_vector += canonical_object_vectors[i] - canonical_utterance_vectors[i]
verb_guidance_vector = verb_guidance_vector / float(len(canonical_utterances))
object_guidance_vector = object_guidance_vector / float(len(canonical_utterances))


def simple_distance(test_cases, action_vectors, distance_measure=spatial.distance.cosine):
    guesses = []
    for t in test_cases:
        guess = {'verb': [], 'obj': []}
        text = t['text']
        vector = infersent.encode([text])[0]

        distances = []
        for a in action_vectors:
            distances.append(distance_measure(a, vector, w=weights))

        for n in range(NUM_MATCHES):
            i = distances.index(min(distances))
            distances[i] = 1000

            guess['verb'].append(actions[i].split(',')[0])
            guess['obj'].append(actions[i].split(',')[1])
        guesses.append(guess)
    return guesses


def translation(test_cases, verb_vectors, object_vectors, verb_guidance_vector, object_guidance_vector, distance_measure=spatial.distance.cosine):
    guesses = []
    for t in test_cases:
        guess = {'verb': [], 'obj': []}
        text = t['text']
        vector = infersent.encode([text])[0]

        verb_distances = []
        for v in verb_vectors:
            verb_distances.append(distance_measure(v, vector + verb_guidance_vector, w=weights))
        for n in range(NUM_MATCHES):
            i = verb_distances.index(min(verb_distances))
            verb = verbs[i]
            verb_distances[i] = 1000
            guess['verb'].append(verb)

        object_distances = []
        for o in object_vectors:
            object_distances.append(distance_measure(o, vector + object_guidance_vector, w=weights))

        for n in range(NUM_MATCHES):
            i = object_distances.index(min(object_distances))
            obj = objects[i]
            object_distances[i] = 1000
            guess['obj'].append(obj)
        guesses.append(guess)
    return guesses


def nearest_neighbor(test_cases, canonical_utterance_vectors, canonical_verbs, canonical_objects, distance_measure=spatial.distance.cosine):
    guesses = []
    for t in test_cases:
        guess = {'verb': [], 'obj': []}

        text = t['text']
        vector = infersent.encode([text])[0]

        distances = []
        for u in canonical_utterance_vectors:
            distances.append(distance_measure(u, vector, w=weights))

        for n in range(NUM_MATCHES):
            i = distances.index(min(distances))
            verb = canonical_verbs[i]
            obj = canonical_objects[i] or ''
            distances[i] = 1000
            guess['verb'].append(verb)
            guess['obj'].append(obj)
        guesses.append(guess)
    return guesses


def pc_distance(test_cases, verb_pcs, object_pcs, distance_measure=spatial.distance.cosine):
    guesses = []
    for t in test_cases:
        guess = {'verb': [], 'obj': []}
        text = t['text']
        vector = infersent.encode([text])[0]

        verb_distances = []
        for j, pc in enumerate(verb_pcs):
            verb_distances.append(distance_measure(pc, vector, w=weights))

        for n in range(NUM_MATCHES):
            i = verb_distances.index(min(verb_distances))
            verb = verbs[i]
            verb_distances[i] = 1000
            guess['verb'].append(verb)

        object_distances = []
        for j, pc in enumerate(object_pcs):
            object_distances.append(distance_measure(pc, vector, w=weights))

        for n in range(NUM_MATCHES):
            i = object_distances.index(min(object_distances))
            obj = objects[i]
            object_distances[i] = 1000
            guess['obj'].append(obj)
        guesses.append(guess)
    return guesses


def method_evaluator(method, method_args):
    guesses = method(*method_args)

    verb_score = 0
    obj_score = 0

    for i, guess in enumerate(guesses):
        t = test_cases[i]
        for v in guess['verb']:
            if v == t['verb']:
                verb_score += 1
                break
        for o in guess['obj']:
            if o == t['obj']:
                obj_score += 1
                break

    print(str(verb_score) + ' ' + str(obj_score))


for measure in weighted_distance_measure_methods:
    method_evaluator(simple_distance, (test_cases, action_vectors, measure))
print()
for measure in weighted_distance_measure_methods:
    method_evaluator(translation, (test_cases, verb_vectors, object_vectors, verb_guidance_vector, object_guidance_vector, measure))
print()
for measure in weighted_distance_measure_methods:
    method_evaluator(nearest_neighbor, (test_cases, canonical_utterance_vectors, canonical_verbs, canonical_objects, measure))
print()
for measure in weighted_distance_measure_methods:
    method_evaluator(pc_distance, (test_cases, verb_pcs, object_pcs, measure))


print('\n\n\n\n')
