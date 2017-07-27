import copy
import json
import nltk
import numpy as np
import operator
from pycorenlp import StanfordCoreNLP
import re
from time import time


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
        normalize_mapping[normalized_ingredient_kv[1].strip()] = ''
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
refine_ingredient_phrase(
    data_path + 'ingredient_list_clean_ingredient_frequency.csv',
    data_path + 'ingredient_list_clean_ingredient_frequency_clean.csv'
)


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


def clean_extracted_ingredient_frequency(fname, measure_word_fname):
    number_pattern = re.compile('(-?)\d+(-?)')
    special_character_pattern = re.compile(
        '\.|,|$|\'|#|`|\(|\)|:|\*|~|%|( -)|=|<|>'
    )
    stemmer = nltk.stem.SnowballStemmer('english')

    ingredient_frequency = np.genfromtxt(fname, dtype=str, delimiter='\t')
    print '#ingredients:', ingredient_frequency.shape

    # read measure words
    measure_word_frequency = np.genfromtxt(measure_word_fname, dtype=str,
                                           delimiter='\t')
    print '#measure words:', measure_word_frequency.shape
    measure_word_set = set()
    for measure_word in measure_word_frequency:
        measure_word_set.add(measure_word[1])

    processed_ingredient_frequency = {}
    t1 = time()
    for index, ingredient_kv in enumerate(ingredient_frequency):
        ingredient_kv[1] = number_pattern.sub('', ingredient_kv[1])
        ingredient_kv[1] = special_character_pattern.sub(' ', ingredient_kv[1])
        ingredient_kv[1] = ingredient_kv[1].strip('- ')
        ingredient_kv[1] = ingredient_kv[1].replace('  ', ' ')
        words = ingredient_kv[1].split(' ')
        normalized_ingredient_words = []
        for word in words:
            if word.islower():
                if word in measure_word_set or word + '.' in measure_word_set:
                    continue
            normalized_ingredient_words.append(stemmer.stem(word))
        normalized_ingredient = ' '.join(sorted(normalized_ingredient_words))
        if normalized_ingredient not in processed_ingredient_frequency.keys():
            processed_ingredient_frequency[normalized_ingredient] = \
                int(ingredient_kv[0])
        else:
            processed_ingredient_frequency[normalized_ingredient] = \
                processed_ingredient_frequency[normalized_ingredient] + \
                int(ingredient_kv[0])
        if index % 10000 == 9999:
            print index, '{:.4f}'.format(time() - t1)
            t1 = time()
    print '#clean ingredients:', len(processed_ingredient_frequency)
    ingredient_sorted = sorted(
        processed_ingredient_frequency.items(),
        key=operator.itemgetter(1), reverse=True
    )
    ofname = fname.replace('.csv', '_clean.csv')
    with open(ofname, 'w') as fout:
        for ingredient_frequency in ingredient_sorted:
            fout.write(str(ingredient_frequency[1]) + '\t' +
                       ingredient_frequency[0] + '\n')
# clean_extracted_ingredient_frequency(
#     data_path + 'ingredient_list_clean_ingredient_frequency.csv',
#     data_path + 'mwf.txt'
# )


def preprocess_stanfordnlp_postag(ingredient_frequency_fname):
    ingredient_frequency = np.genfromtxt(ingredient_frequency_fname,
                                         dtype=str, delimiter='\t')
    print 'ingredient frequency shape:', ingredient_frequency.shape
    ingredient_lines = []
    for ingredient_kv in ingredient_frequency:
        # '\.|,|$|\'|#|`|\(|\)|:|\*|~|%|( -)|='
        clean_text = ingredient_kv[1]
        clean_text = clean_text.replace('$', ' $ ')
        clean_text = clean_text.replace('#', ' # ')
        clean_text = clean_text.replace('%', ' % ')
        clean_text = clean_text.replace('*', ' * ')
        clean_text = clean_text.replace(':', ' : ')
        clean_text = clean_text.replace('~', ' ~ ')
        ingredient_lines.append(clean_text + ' .\n')
    with open(ingredient_frequency_fname.replace('csv', 'txt'), 'w') as fout:
        fout.writelines(ingredient_lines)
# preprocess_stanfordnlp_postag(
#     data_path + 'ingredient_list_clean_ingredient_frequency.csv'
# )