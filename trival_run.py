import copy
import json
import nltk
import numpy as np
from pycorenlp import StanfordCoreNLP
import re


def refine_measure_word(fname):
    number_pattern = re.compile('\d+')
    measure_word_frequency = np.genfromtxt(fname, dtype=str, delimiter='\t')
    print 'data shape:', measure_word_frequency.shape
    high_confidence_words = set()
    for i in xrange(50):
        high_confidence_words.add(measure_word_frequency[i][1])

    refined_measure_word_frequency = []
    for word_frequency in measure_word_frequency:
        if int(word_frequency[0]) > 21:
            refined_measure_word_frequency.append(word_frequency)
        elif word_frequency[1][-1] == '.':
            refined_measure_word_frequency.append(word_frequency)
        else:
            clean_text = number_pattern.sub(
                '', word_frequency[1].replace('.', '').replace('-', '').
                    replace('/', '').strip()
            )
            if clean_text in high_confidence_words:
                refined_measure_word_frequency.append(word_frequency)
    print '#selected words:', len(refined_measure_word_frequency)
    ofname = fname.replace('.csv', '_rule.csv')
    with open(ofname, 'w') as fout:
        for word_frequency in refined_measure_word_frequency:
            fout.write(word_frequency[0] + '\t' + word_frequency[1] + '\n')
# refine_measure_word(
#     '/home/ffl/nus/MM/recipe/data/ingredient_list_measure_word_frequency.csv'
# )


def refine_ingredient_phrase(ingredient_frequency_fname,
                             normalized_ingredient_frequency_fname):
    ingredient_frequency = np.genfromtxt(ingredient_frequency_fname,
                                         dtype=str, delimiter='\t')
    print 'ingredient frequency shape:', ingredient_frequency.shape
    normalized_ingredient_frequency = np.genfromtxt(
        normalized_ingredient_frequency_fname, dtype=str, delimiter='\t'
    )
    print 'normalized ingredient frequency shape:', \
        normalized_ingredient_frequency.shape
    normalize_mapping = {}
    max_length = 0
    for normalized_ingredient_kv in normalized_ingredient_frequency:
        normalize_mapping[normalized_ingredient_kv[1]] = ''
        if len(normalized_ingredient_kv[1].strip()) > max_length:
            max_length = len(normalized_ingredient_kv[1].strip())
    print 'maximum length:', max_length
    stemmer = nltk.stem.SnowballStemmer('english')
    for ingredient_kv in ingredient_frequency:
        words = ingredient_kv[1].strip().split()
        if words is not None:
            normalized_words = []
            for postagged_word in words:
                normalized_words.append(
                    stemmer.stem(postagged_word)
                )
            normalized_text = ' '.join(sorted(normalized_words))
            normalize_mapping[normalized_text] = copy.copy(ingredient_kv[1])
    for index, normalized_ingredient_kv in \
            enumerate(normalized_ingredient_frequency):
        print str(normalized_ingredient_kv[0]) + '\t' +\
              ('{:' + str(max_length) + '}').format(
                  normalized_ingredient_kv[1].strip()) + '\t' +\
              normalize_mapping[normalized_ingredient_kv[1].strip()]
        # if index > 20:
        #     break
data_path = '/home/ffl/nus/MM/recipe/data/'
# refine_ingredient_phrase(
#     data_path + 'ingredient_list_ingredient_frequency.csv',
#     data_path + 'ingredient_list_ingredient_normalized_frequency.csv'
# )


def test_stanford_nlp():
    nlp = StanfordCoreNLP('http://localhost:9000')
    text = (
        '1 tablespoon tomato paste. '
        '1/2 cup freshly grated Pecorino Romano cheese. plus more for sprinkling. '
        'Salt and freshly ground pepper. '
        '2 1/2 cups prepared tomato sauce. '
        '1 tsp. molasses.'
    )
    # text = (
    #     'Pusheen and Smitha walked along the beach. '
    #     'Pusheen wanted to surf, but fell off the surfboard.')
    # output = nlp.annotate(text, properties={
    #     'annotators': 'tokenize,ssplit,pos,depparse,parse',
    #     'outputFormat': 'json'
    # })
    output = nlp.annotate(text, properties={
        'annotators': 'pos,lemma',
        'outputFormat': 'json'
    })
    print output
    with open('temp_1.json', 'w') as fout:
        json.dump(output, fout)
# test_stanford_nlp()


def preprocess_stanfordnlp_postag(ingredient_frequency_fname):
    ingredient_frequency = np.genfromtxt(ingredient_frequency_fname,
                                         dtype=str, delimiter='\t')
    print 'ingredient frequency shape:', ingredient_frequency.shape
    ingredient_lines = []
    for ingredient_kv in ingredient_frequency:
        ingredient_lines.append(ingredient_kv[1].replace('.', '') + ' .\n')
    with open(ingredient_frequency_fname.replace('csv', 'txt'), 'w') as fout:
        fout.writelines(ingredient_lines)
# preprocess_stanfordnlp_postag(
#     data_path + 'ingredient_list_ingredient_frequency.csv'
# )

