"""
This file holds functions for words loading and processing.
"""

import collections
import pathlib


def load_word_dict(
        wordlist_path: pathlib.Path,
        max_word_len: int,
        only_ascii: bool = True,
        only_alpha: bool = True) -> collections.OrderedDict[str, None]:
    """
    Loads wordlist to OrderedDict and maintains the order of words from the sorce file.
    Automatically converts all words to lower case.

    Args:
        wordlist_path: A path to the file with words.
            It requires one word per line.
        max_word_len: Maximum word length (inclusive) that will be loaded.
        only_ascii: Load only words where all the characters are ASCII.
        only_alpha: Load only words where all the characters are
            alphabet letters (a-z).

    Returns: Words that satisfied the requirements.
    """
    word_dict = collections.OrderedDict()
    with open(wordlist_path, "r", encoding="utf-8") as wordlist_file:
        for line in wordlist_file:
            word = line.strip()
            word = word.lower()  # I want to force lowercase letters.
            if len(word) > max_word_len:
                continue
            # This nested if is done for better readability / maintainability
            if only_ascii and word.isascii():
                if only_alpha and word.isalpha():
                    word_dict[word] = None
                elif not only_alpha:
                    word_dict[word] = None
            elif not only_ascii:
                if only_alpha and word.isalpha():
                    word_dict[word] = None
                elif not only_alpha:
                    word_dict[word] = None
    return word_dict


def contains_letters(string_1: str, string_2: str) -> bool:
    """
    Check if all the letters of string_1 are also in string_2.

    Args:
        string_1: String letters are checked against string_2
        string_2: String that is provided as target.

    Returns: True if all the letters in string_1 are also present in string_2
    """
    letters_counter = collections.Counter(string_2)
    for letter in string_1:
        if letter in letters_counter and letters_counter[letter] > 0:
            letters_counter[letter] -= 1
        else:
            return False
    return True


def remove_impossible_words(word_dict: collections.OrderedDict,
                            anagram: str) -> collections.OrderedDict:
    """
    Removes words that cannot be a part of the anagram.

    Args:
        word_dict: Dict of words.
        anagram: Letters that specifies anagram requirements.

    Return: New filtered OrderedDict containing only words
        that can by part of an anagram.
    """
    new_word_dict = collections.OrderedDict()
    for word in word_dict.keys():
        if contains_letters(word, anagram):
            new_word_dict[word] = None
    return new_word_dict
