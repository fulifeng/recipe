from bintrees import FastAVLTree as avltree
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

class ingredient_extractor:
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
        # # (JJ | VBD | VBN) ? ((CC | ,) ? (JJ | VBD | VBN)) * ?
        # # (NN | NNS | NNP | NNPS) +
        # self.ingredient_pattern = re.compile(
        #     '((A|,)?(G|c|e))*?(M|N|L|O)+')
        # JJ ? ((CC | ,) ? JJ) * ?
        # (NN | NNS | NNP | NNPS) +
        self.ingredient_pattern = re.compile(
            '((A|,)?G)*?(M|N|L|O)+')
        self.measure_word_pattern = re.compile('B(M|N|L|O)\.?F?(M|N|L|O)')
        self.pure_noun_phrase_pattern = re.compile('(M|N|L|O)+')
        self.range_number_pattern = re.compile('-\d+')

        with open(self.fname) as fin:
            self.ingredient_list = fin.readlines()
        print '#lines in ingredient list:', len(self.ingredient_list)

    def count_words(self):
        ingredient_count_by_length = [0] * 101
        for ingredient_string in self.ingredient_list:
            ingredient_string = self.bracket_pattern.sub('', ingredient_string)
            ingredient_string.replace('  ', ' ').strip()
            words = ingredient_string.split(' ')
            if len(words) >= 100:
                ingredient_count_by_length[100] += 1
            else:
                ingredient_count_by_length[len(words)] += 1
        ingredient_short_than = 0
        ingredient_count = len(self.ingredient_list)
        for i in xrange(0, 101):
            ingredient_short_than += ingredient_count_by_length[i]
            print i, '\t', ingredient_count_by_length[i], '\t', \
                float(ingredient_short_than) / ingredient_count

    def check_measure_words(self, measure_word_fname):
        # read measure word
        measure_word_frequency = np.genfromtxt(measure_word_fname, dtype=str,
                                               delimiter='\t')
        print 'data shape:', measure_word_frequency.shape
        measure_word_set = set()
        for measure_word in measure_word_frequency:
            measure_word_set.add(measure_word[1])
        problematic_mearure_words = set()
        ingredient_skipped = 0
        for index, ingredient_string in enumerate(self.ingredient_list):
            ingredient_string = self.bracket_pattern.sub(
                '', ingredient_string.strip()
            )
            ingredient_string = self.range_number_pattern.sub(
                '', ingredient_string
            )
            # print ingredient_string
            tokenized_ingredient = nltk.word_tokenize(ingredient_string)
            if len(tokenized_ingredient) > 20:
                print index
                ingredient_skipped += 1
                continue
            postagged_ingredient_words = nltk.pos_tag(tokenized_ingredient)
            measure_word_index = -1
            measure_word = None
            for word_index, ingredient_word_postag in \
                    enumerate(postagged_ingredient_words):
                if ingredient_word_postag[0] in measure_word_set or \
                                        ingredient_word_postag[
                                            0] + '.' in measure_word_set:
                    measure_word_index = word_index
                    measure_word = copy.copy(ingredient_word_postag[0])
                    break
            start_index = 0
            # the third condition is used to handle part of the unreliable
            # measure words as the last word couldn't be a measure word.
            if measure_word_index == -1 or measure_word_index > 3:
                number_index = -1
                for word_index, ingredient_word_postag in \
                        enumerate(postagged_ingredient_words):
                    if ingredient_word_postag[1] == 'CD':
                        number_index = word_index
                        break
                if number_index == -1:
                    start_index = 0
                else:
                    start_index = number_index + 1
            else:
                start_index = measure_word_index + 1

            if not start_index < len(postagged_ingredient_words):
                print index, 'unexpected start index:', start_index, \
                    postagged_ingredient_words
                if not measure_word is None:
                    problematic_mearure_words.add(measure_word)
                    problematic_mearure_words.add(measure_word + '.')
                continue

        for word in problematic_mearure_words:
            print word

    # @profile
    def construct_ingredient_vocabulary(self, measure_word_fname):
        # read measure word
        measure_word_frequency = np.genfromtxt(measure_word_fname, dtype=str,
                                               delimiter='\t')
        print 'data shape:', measure_word_frequency.shape
        measure_word_set = set()
        for measure_word in measure_word_frequency:
            measure_word_set.add(measure_word[1])
        ingredient_list = []
        ingredient_frequency_dict = {}
        # ingredient_frequency_dict = avltree()
        normalized_ingredient_list = []
        normalized_ingredient_frequency_dict = {}
        # normalized_ingredient_frequency_dict = avltree()
        # noun_ingredient_list = []
        # noun_ingredient_frequency_dict = {}
        # normalized_noun_ingredient_list = []
        # normalized_noun_ingredient_frequency_dict = {}
        ingredient_skipped = 0
        for index, ingredient_string in enumerate(self.ingredient_list):
            # ingredient_string = self.bracket_pattern.sub(
            #     '', ingredient_string.strip()
            # )
            # ingredient_string = self.range_number_pattern.sub(
            #     '', ingredient_string
            # )
            # print ingredient_string
            tokenized_ingredient = nltk.word_tokenize(ingredient_string)
            if len(tokenized_ingredient) > 20:
                print index
                ingredient_skipped += 1
                continue
            postagged_ingredient_words = nltk.pos_tag(tokenized_ingredient)
            measure_word_index = -1
            for word_index, ingredient_word_postag in \
                    enumerate(postagged_ingredient_words):
                if ingredient_word_postag[0] in measure_word_set or \
                    ingredient_word_postag[0] + '.' in measure_word_set:
                    measure_word_index = word_index
                    break
            start_index = 0
            # the third condition is used to handle part of the unreliable
            # measure words as the last word couldn't be a measure word.
            if measure_word_index == -1 or measure_word_index > 3 or \
                    measure_word_index == len(postagged_ingredient_words):
                number_index = -1
                for word_index, ingredient_word_postag in \
                        enumerate(postagged_ingredient_words):
                    if ingredient_word_postag[1] == 'CD':
                        number_index = word_index
                        break
                if number_index == -1 or number_index > 2:
                    start_index = 0
                else:
                    start_index = number_index + 1
            else:
                start_index = measure_word_index + 1

            if not start_index < len(postagged_ingredient_words):
                print 'unexpected start index:', start_index, \
                    postagged_ingredient_words
                ingredient_skipped += 1
                continue
            # print postagged_ingredient_words
            # print measure_word_index, start_index
            pos_label_string = self._get_pos_lable_string(
                postagged_ingredient_words[start_index:]
            )
            # print postagged_ingredient_words[start_index:]
            # print pos_label_string
            # with description
            matches = self.ingredient_pattern.finditer(pos_label_string)
            # pure noun phrase
            # matches = self.pure_noun_phrase_pattern.finditer(pos_label_string)
            is_first = True
            for match in matches:
                # print match.span()
                # print postagged_ingredient_words[match.start():match.end()]
                # print index
                ingredient_text = ' '.join(
                    tokenized_ingredient[start_index + match.start():\
                        start_index + match.end()])
                # print start_index, match.start(), match.end()
                if is_first:
                    print index, ingredient_text
                    is_first = False
                else:
                    continue
                ingredient_text += '\n'
                ingredient_list.append(ingredient_text)
                # print index, ingredient_text
                if ingredient_text not in ingredient_frequency_dict.keys():
                    ingredient_frequency_dict[ingredient_text] = 1
                else:
                    ingredient_frequency_dict[ingredient_text] = \
                        ingredient_frequency_dict[ingredient_text] + 1
                normalized_ingredient_words = self._normalize_ingredient_words(
                    postagged_ingredient_words[start_index + match.start():\
                        start_index + match.end()]
                )
                # print 'normalized:', normalized_ingredient_words
                ingredient_text = ' '.join(normalized_ingredient_words)
                ingredient_text += '\n'
                normalized_ingredient_list.append(copy.copy(ingredient_text))
                # print normalized_ingredient_words
                # print 'sorted:', sorted(normalized_ingredient_words)
                normalized_ingredient_word_ordered = \
                    ' '.join(sorted(normalized_ingredient_words))
                # print index, ingredient_text
                # print index, normalized_ingredient_word_ordered
                # print normalized_ingredient_word_ordered
                normalized_ingredient_word_ordered += '\n'
                if normalized_ingredient_word_ordered not in \
                        normalized_ingredient_frequency_dict:
                    normalized_ingredient_frequency_dict[
                        normalized_ingredient_word_ordered] = 1
                else:
                    normalized_ingredient_frequency_dict[
                        normalized_ingredient_word_ordered] = \
                        normalized_ingredient_frequency_dict[
                            normalized_ingredient_word_ordered] + 1
                    # TEST
            # if index > 20:
            #     break
        print '#ingredient lines skipped:', ingredient_skipped
        ofname = self.fname.replace('.txt', '_ingredient_list.txt')
        with open(ofname, 'w') as fout:
            fout.writelines(ingredient_list)

        ingredient_sorted = sorted(
            ingredient_frequency_dict.items(), key=operator.itemgetter(1),
            reverse=True
        )
        ofname = self.fname.replace('.txt', '_ingredient_frequency.csv')
        with open(ofname, 'w') as fout:
            for ingredient_frequency in ingredient_sorted:
                fout.write(str(ingredient_frequency[1]) + '\t' +
                           ingredient_frequency[0])

        ofname = self.fname.replace('.txt', '_ingredient_list_normalized.txt')
        with open(ofname, 'w') as fout:
            fout.writelines(normalized_ingredient_list)

        ingredient_sorted = sorted(
            normalized_ingredient_frequency_dict.items(),
            key=operator.itemgetter(1), reverse=True
        )
        ofname = self.fname.replace('.txt',
                                    '_ingredient_normalized_frequency.csv')
        with open(ofname, 'w') as fout:
            for ingredient_frequency in ingredient_sorted:
                fout.write(str(ingredient_frequency[1]) + '\t' +
                           ingredient_frequency[0])

    def extract_ingredient(self, measure_word_fname):
        # read measure word
        measure_word_frequency = np.genfromtxt(measure_word_fname, dtype=str,
                                               delimiter='\t')
        print 'data shape:', measure_word_frequency.shape
        measure_word_set = set()
        for measure_word in measure_word_frequency:
            measure_word_set.add(measure_word[1])
        ingredient_phrase_set = set()
        ingredient_skipped = 0
        for index, ingredient_string in enumerate(self.ingredient_list):
            ingredient_string = self.bracket_pattern.sub(
                '', ingredient_string.strip()
            )
            ingredient_string = self.range_number_pattern.sub(
                '', ingredient_string
            )
            # print ingredient_string
            tokenized_ingredient = nltk.word_tokenize(ingredient_string)
            postagged_ingredient_words = nltk.pos_tag(tokenized_ingredient)
            # print postagged_ingredient_words
            pos_label_string = self._get_pos_lable_string(
                postagged_ingredient_words
            )
            matches = self.pure_noun_phrase_pattern.finditer(pos_label_string)
            for match in matches:
                ingredient_words = []
                normalized_ingredient_words = []
                for i in range(match.start(), match.end()):
                    # check whether the word is a measure word q
                    ingredient_words.append(tokenized_ingredient[i])

                ingredient_text = ' '.join(
                    tokenized_ingredient[match.start():match.end()])
                ingredient_text += '\n'
                # print index, ingredient_text
                normalized_ingredient_words = self._normalize_ingredient_words(
                    postagged_ingredient_words[match.start():\
                        match.end()]
                )
                # print 'normalized:', normalized_ingredient_words
                ingredient_text = ' '.join(normalized_ingredient_words)
                ingredient_text += '\n'
                normalized_ingredient_list.append(copy.copy(ingredient_text))
                # print normalized_ingredient_words
                # print 'sorted:', sorted(normalized_ingredient_words)
                normalized_ingredient_word_ordered = \
                    ' '.join(sorted(normalized_ingredient_words))
                # print index, ingredient_text
                # print index, normalized_ingredient_word_ordered
                # print normalized_ingredient_word_ordered
                normalized_ingredient_word_ordered += '\n'
                if normalized_ingredient_word_ordered not in \
                        normalized_ingredient_frequency_dict:
                    normalized_ingredient_frequency_dict[
                        normalized_ingredient_word_ordered] = 1
                else:
                    normalized_ingredient_frequency_dict[
                        normalized_ingredient_word_ordered] = \
                        normalized_ingredient_frequency_dict[
                            normalized_ingredient_word_ordered] + 1
                    # TEST
            # if index > 20:
            #     break
        print '#ingredient lines skipped:', ingredient_skipped

    def extract_measure_word(self):
        measure_word_list = []
        measure_word_frequency_dict = {}
        for index, ingredient_string in enumerate(self.ingredient_list):
            ingredient_string = self.bracket_pattern.sub(
                '', ingredient_string.strip()
            )
            ingredient_string = self.range_number_pattern.sub(
                '', ingredient_string
            )
            tokenized_ingredient = nltk.word_tokenize(ingredient_string)
            postagged_ingredient_words = nltk.pos_tag(tokenized_ingredient)

            # print postagged_ingredient_words
            pos_label_string = self._get_pos_lable_string(
                postagged_ingredient_words
            )
            # print pos_label_string
            matches = self.measure_word_pattern.finditer(pos_label_string)
            for match in matches:
                # print match.span()
                # print postagged_ingredient_words[match.start():match.end()]
                # print index
                measure_word = postagged_ingredient_words[match.start() + 1][0]
                if postagged_ingredient_words[match.start() + 2][0] == '.':
                    measure_word += '.'
                print index, measure_word
                measure_word += '\n'
                measure_word_list.append(measure_word)
                if measure_word not in measure_word_frequency_dict.keys():
                    measure_word_frequency_dict[measure_word] = 1
                else:
                    measure_word_frequency_dict[measure_word] = \
                        measure_word_frequency_dict[measure_word] + 1
            # # TEST
            # if index > 1000:
            #     break
        ofname = self.fname.replace('.txt', '_measure_word_list.txt')
        with open(ofname, 'w') as fout:
            fout.writelines(measure_word_list)

        measure_word_frequency_sorted = sorted(
            measure_word_frequency_dict.items(), key=operator.itemgetter(1),
            reverse=True
        )
        ofname = self.fname.replace('.txt', '_measure_word_frequency.csv')
        with open(ofname, 'w') as fout:
            for measure_work_frequency in measure_word_frequency_sorted:
                fout.write(str(measure_work_frequency[1]) + '\t' +
                           measure_work_frequency[0])

    def pos_tagging(self):
        for index, ingredient_string in enumerate(self.ingredient_list):
            ingredient_string = self.bracket_pattern.sub(
                '', ingredient_string.strip()
            )
            ingredient_string = self.range_number_pattern.sub(
                '', ingredient_string
            )
            tokenized_ingredient = nltk.word_tokenize(ingredient_string)
            postagged_ingredient_words = nltk.pos_tag(tokenized_ingredient)


    def _get_pos_lable_string(self, postagged_ingredient_words):
        pos_label_string = ''
        for postagged_ingredient_word in postagged_ingredient_words:
            if postagged_ingredient_word[1] in self.pos_tag_dict.keys():
                pos_label_string += self.pos_tag_dict[
                    postagged_ingredient_word[1]]
            # elif postagged_ingredient_word[1] == '.' or \
            #                 postagged_ingredient_word[1] == ',':
            else:
                pos_label_string += postagged_ingredient_word[1]
        return pos_label_string

    def _normalize_ingredient_words(self, postagged_ingredient_words):
        normalized_words = []
        for postagged_word in postagged_ingredient_words:
            if not postagged_word[1] in self.pos_tag_undefined:
                normalized_words.append(
                    self.stemmer.stem(postagged_word[0])
                )
        return normalized_words


if __name__ == '__main__':
    # fname = '/home/ffl/nus/MM/recipe/data/ingredient_list_10k_clean.txt'
    # fname = '/home/ffl/nus/MM/recipe/data/ingredient_list_100k.txt'
    fname = '/home/ffl/nus/MM/recipe/data/ingredient_list_clean.txt'
    extractor = ingredient_extractor(fname)
    # extractor.extract_measure_word()
    # extractor.count_words()
    # extractor.extract_ingredient('/home/ffl/nus/MM/recipe/data/mwf_test.csv')
    # extractor.construct_ingredient_vocabulary(
    #     '/home/ffl/nus/MM/recipe/data/mwf.txt'
    # )
    # extractor.check_measure_words(
    #     '/home/ffl/nus/MM/recipe/data/mwf.txt'
    # )
    extractor.construct_ingredient_vocabulary(
        '/home/ffl/nus/MM/recipe/data/mwf.txt'
    )