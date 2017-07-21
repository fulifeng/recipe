import copy
import json
import numpy as np
import nltk
import operator
import re
try:
    set
except NameError:
    from sets import Set as set


class IngredientProcessor(object):
    def __init__(self, fname):
        self.fname = fname
        self.ingredient_list = []
        self.pos_tag_list = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR',
                             'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS',
                             'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS',
                             'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG',
                             'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
        self.pos_tag_dict = {}
        pos_tag_label = 'A'
        for pos_tag in self.pos_tag_list:
            self.pos_tag_dict[pos_tag] = pos_tag_label
            pos_tag_label = chr(ord(pos_tag_label) + 1)
            if pos_tag_label == 'Z':
                pos_tag_label = 'a'
        # for pos_tag_kv in self.pos_tag_dict.iteritems():
        #     print pos_tag_kv[0], pos_tag_kv[1]
        self.pos_tag_undefined = set([',', '.', '$', ':', '\'\'', '#', '``',
                                      '(', ')'])
        self.stemmer = nltk.stem.SnowballStemmer('english')

        self.bracket_pattern = re.compile('\(.*?\)')
        # (JJ | VBD | VBN) ? ((CC | ,) ? (JJ | VBD | VBN)) * ?
        # (NN | NNS | NNP | NNPS) +
        self.ingredient_pattern = re.compile(
            '((A|,)?(G|c|e))*?(M|N|L|O)+')
        self.measure_word_pattern = re.compile('B(M|N|L|O)\.?F?(M|N|L|O)')
        self.pure_noun_phrase_pattern = re.compile('(M|N|L|O)+')
        self.range_number_pattern = re.compile('-\d+')

        with open(self.fname) as fin:
            self.ingredient_list = fin.readlines()
        print '#lines in ingredient list:', len(self.ingredient_list)

    # def clean_ingredient_text(self):
    #     pass