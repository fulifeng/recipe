import copy
import json
import numpy as np
import operator

from ingredient import IngredientProcessor

class IngredientPostprocessor(IngredientProcessor):
    def __init__(self, fname):
        super(IngredientPostprocessor, self).__init__(fname)

    '''
    In file with name self.fname, we store the pure text of ingredient phrases
    extracted by 'construct_ingredient_vocabulary'.
    In file with name self.fname.replace('txt', 'csv'), we store the
    ingredient phrases with frequency. It is one of output files of
    'construct_ingredient_vocabulary'.
    File with name self.fname + '.json' is the output file of Stanford POS
    tagger while tagging self.fname.
    Here we re-extract "JJ ? ((CC | ,) ? JJ) * ? # (NN | NNS | NNP | NNPS) +"
    from the extracted ingredient phrases to handle problematic phrases caused
    by POS-tagging errors of the NLTK tagger, especially the and/or error and
    punctuation error.
    '''
    def postprocess_ingredient_frequency(self):
        # read tagging output of Stanford POS tagger
        postagged_ingredient_phrases = []
        with open(self.fname + '.json') as fin:
            data = json.load(fin)
            print '#sentences', len(data['sentences'])
            for sentences in data['sentences']:
                tokens = []
                postag_str = ''
                tags = []
                for tagged_token in sentences['tokens']:
                    tokens.append(tagged_token['word'])
                    tag = tagged_token['pos']
                    if tag in self.pos_tag_dict.keys():
                        postag_str += self.pos_tag_dict[tag]
                    else:
                        postag_str += tag
                    tags.append(tag)
                postagged_ingredient_phrases.append(
                    # copy.copy((postag_str, tokens))
                    copy.copy((postag_str, tokens, tags))
                )
        print '#tagged phrases:', len(postagged_ingredient_phrases)

        # read frequency
        ingredient_frequency = np.genfromtxt(self.fname.replace('txt', 'csv'),
                                             dtype=str, delimiter='\t')
        print '#ingredients:', ingredient_frequency.shape

        assert ingredient_frequency.shape[0] == \
               len(postagged_ingredient_phrases), 'lengths don\'t match'

        ingredient_list = []
        ingredient_frequency_dict = {}
        for index, postagged_ingredient in \
                enumerate(postagged_ingredient_phrases):
            matches = self.ingredient_pattern.finditer(postagged_ingredient[0])
            print postagged_ingredient[1]
            print postagged_ingredient[2]
            for match in matches:
                # print match.span()
                # print postagged_ingredient_words[match.start():match.end()]
                # print index
                ingredient_text = ' '.join(
                    postagged_ingredient[1][match.start():match.end()])
                # print start_index, match.start(), match.end()
                ingredient_text += '\n'
                ingredient_list.append(ingredient_text)
                # print index, ingredient_text
                if ingredient_text not in ingredient_frequency_dict.keys():
                    ingredient_frequency_dict[ingredient_text] = \
                        int(ingredient_frequency[index][0])
                else:
                    ingredient_frequency_dict[ingredient_text] = \
                        ingredient_frequency_dict[ingredient_text] + \
                        int(ingredient_frequency[index][0])
                print index, ingredient_text.strip()
                break
            # TEST
            if index > 300:
                break
        ofname = self.fname.replace('.txt', '_re-extract.txt')
        with open(ofname, 'w') as fout:
            fout.writelines(ingredient_list)

        ingredient_sorted = sorted(
            ingredient_frequency_dict.items(), key=operator.itemgetter(1),
            reverse=True
        )
        ofname = self.fname.replace('.txt', '_re-extract.csv')
        with open(ofname, 'w') as fout:
            for ingredient_frequency in ingredient_sorted:
                fout.write(str(ingredient_frequency[1]) + '\t' +
                           ingredient_frequency[0])

if __name__ == '__main__':
    fname = '/home/ffl/nus/MM/recipe/data/' \
            'ingredient_list_clean_ingredient_frequency.txt'
    preprocessor = IngredientPostprocessor(fname)
    preprocessor.postprocess_ingredient_frequency()