from itertools import tee
import unidecode
import numpy as np

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def love_compute(name_1, name_2, word, normalize=False, string=None):
    if not string:
        string = get_name_num(name_1, name_2, word)
    output = ""
    for a, b in pairwise(string):
        c = int(a) + int(b)
        if len(str(c)) != 1:
            c = int(str(c)[0]) + int(str(c)[1])
        output += str(c)
    if len(output) > 2:
        output = love_compute(name_1, name_2, word, normalize=False, string=output)
    if normalize:
        X_std = (int(output) - 11) / (99 - 11)
        X_scaled = X_std * (100 - 0) + 0
        final_output = np.around(X_scaled, 0)
        output = str(int(final_output)) + "%"
    return output

def get_name_num(name_1, name_2, word):
    name_1 = unidecode.unidecode(name_1).lower()
    name_2 = unidecode.unidecode(name_2).lower()
    word = unidecode.unidecode(word).lower()
    chr_list = ""
    base = word
    name = "".join(set(base)) + name_1 + name_2
    for b in base:
        n = 0
        for chr_ in name:
            if chr_ == b:
                n += 1
        chr_list += str(n)
    return chr_list
