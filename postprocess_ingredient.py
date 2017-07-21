import copy
import nltk
import re
from ingredient import IngredientProcessor

class IngredientPostprocessor(IngredientProcessor):
    def __init__(self, fname):
        super(IngredientPostprocessor, self).__init__(fname)
        self.number_pattern = re.compile('\d+')
        self.special_character_pattern = re.compile('\.|,|$|\'|#|`|\(|\)')
