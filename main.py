#! /usr/bin/env python3
import hashlib
import collections
import pathlib
from typing import Dict


def load_word_dict(word_dict_path: pathlib.Path,
                   max_len: int,
                   only_ascii: bool = True,
                   only_alpha: bool = True) -> collections.OrderedDict:
    word_dict = collections.OrderedDict()
    with open(word_dict_path, "r") as f:
        for line in f:
            word = line.strip()
            word = word.lower()
            if len(word) > max_len: continue
            if only_ascii and word.isascii():
                if only_alpha and word.isalpha():
                    word_dict[word] = True
                elif not only_alpha:
                    word_dict[word] = True
            elif not only_ascii:
                if only_alpha and word.isalpha():
                    word_dict[word] = True
                elif not only_alpha:
                    word_dict[word] = True
    return word_dict

def contains_letters(string_1: str, string_2: str) -> bool:
    anagram_counter = collections.Counter(string_2)
    for char in string_1:
        if char in anagram_counter and anagram_counter[char] > 0:
            anagram_counter[char] -= 1
        else:
            return False
    return True

def remove_impossible_words(word_dict: collections.OrderedDict, anagram: str) -> collections.OrderedDict:
    new_word_dict = collections.OrderedDict()
    for word in word_dict.keys():
        if contains_letters(word, anagram):
            new_word_dict[word] = collections.Counter(word)
    return new_word_dict

def main():
    anagram = "poultry outwits ants".replace(" ", "")
    only_ascii = False
    only_alpha = False
    max_len = len(anagram)
    if anagram.isascii():
        only_ascii = True
    if anagram.isalpha():
        only_alpha = True
    current_dir = pathlib.Path().resolve()
    word_dict_path = current_dir.joinpath("wordlist")
    word_dict = load_word_dict(word_dict_path, max_len, only_ascii, only_alpha)
    print(len(word_dict))
    print(list(word_dict.keys())[len(word_dict) - 10:])

    word_dict = remove_impossible_words(word_dict, anagram)
    print(word_dict)
    print(len(word_dict))




if __name__ == "__main__":
    main()