import collections
import re
import string
from itertools import chain
import pprint


# retrieve and print the most common keywords
def get_description_keywords(descriptions):
    # merge 'descriptions', which is a list of sets, to a single list.
    # this ensures that each keyword appears only once from each job listing,
    # thus avoiding skewing the results.
    words = [item for sublist in descriptions for item in sublist]

    # ignore words from english_words.txt
    ignore_list = get_common_words_list()
    words = [x for x in words if x not in ignore_list]

    most_common = collections.Counter(words).most_common(50)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(most_common)


def get_common_words_list():
    f = open('english_words.txt')
    english_words = []

    for word in f.read().split():
        english_words.append(word)

    return english_words

