import copy
import re
from ingredient import IngredientProcessor

class IngredientPreprocessor(IngredientProcessor):
    def __init__(self, fname):
        super(IngredientPreprocessor, self).__init__(fname)
        self.special_number_pattern = re.compile('(-|/)\d+')
        self.bracket_pattern = re.compile('(\(.*?\))|(\[.*?\])|(<.*?>)')
        # self.round_bracket_pattern = re.compile('\(.*?\)')
        self.half_bracket_pattern = re.compile('(.*?(\)|\]|>))|(\(|\[|<).*')
        self.special_character_pattern = re.compile('\.')

    # remove special characters, contents surrounded by bracket or text
    # boundary ('....)' or '(....')
    def clean_ingredient_text(self):
        for index, ingredient_line in enumerate(self.ingredient_list):
            ingredient_string = self.bracket_pattern.sub(
                '', ingredient_line.strip()
            )
            ingredient_string = self.half_bracket_pattern.sub(
                '', ingredient_string
            )
            ingredient_string = self.special_number_pattern.sub(
                '', ingredient_string
            )
            ingredient_string = self.special_character_pattern.sub(
                ' ', ingredient_string
            )
            ingredient_string = ingredient_string.replace('/', ' / ')
            self.ingredient_list[index] = copy.copy(ingredient_string)
        with open(self.fname.replace('.txt', '_clean.txt'), 'w') as fout:
            for ingredient_line in self.ingredient_list:
                fout.write(ingredient_line + '\n')

if __name__ == '__main__':
    # fname = '/home/ffl/nus/MM/recipe/data/ingredient_list_10k.txt'
    # fname = '/home/ffl/nus/MM/recipe/data/ingredient_list_100k.txt'
    fname = '/home/ffl/nus/MM/recipe/data/ingredient_list.txt'
    preprocessor = IngredientPreprocessor(fname)
    preprocessor.clean_ingredient_text()