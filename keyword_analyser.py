import collections
import re
import string


def get_description_keywords(descriptions):
    words = re.findall(r'\w+', descriptions.lower())
    ignore = get_common_words_list()

    words = [x for x in words if x not in ignore]

    most_common = collections.Counter(words).most_common(50)
    print(most_common)

def get_common_words_list():
    f = open('english_words.txt')
    english_words =[]
    for word in f.read().split():
        english_words.append(word)

    return english_words

