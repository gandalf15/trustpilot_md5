#! /usr/bin/env python3
import hashlib
import collections
import pathlib
import time
from typing import Dict, Tuple
import trie
import multiprocessing as mp


def load_word_dict(word_dict_path: pathlib.Path,
                   max_word_len: int,
                   only_ascii: bool = True,
                   only_alpha: bool = True) -> collections.OrderedDict:
    word_dict = collections.OrderedDict()
    with open(word_dict_path, "r") as f:
        for line in f:
            word = line.strip()
            word = word.lower()
            if len(word) > max_word_len: continue
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
    for letter in string_1:
        if letter in anagram_counter and anagram_counter[letter] > 0:
            anagram_counter[letter] -= 1
        else:
            return False
    return True


def remove_impossible_words(word_dict: collections.OrderedDict,
                            anagram: str) -> collections.OrderedDict:
    new_word_dict = collections.OrderedDict()
    for word in word_dict.keys():
        if contains_letters(word, anagram):
            new_word_dict[word] = True
    return new_word_dict


def check_hash(anagrams_queue: mp.Queue, target_hashes: Dict):
    remaining_targets = list(target_hashes.keys())
    counter = 0
    start_time = time.time()
    while len(remaining_targets) > 0:
        anagram = anagrams_queue.get()
        anagrams_queue.task_done()
        if anagram is None:
            break
        counter += 1
        if counter % 5000 == 0:
            print("Checked:", counter, "anagrams but haven't found yet!")
        md5_hash = hashlib.md5(anagram.encode('utf-8'))
        md5_hash_hex = md5_hash.hexdigest()
        if md5_hash_hex in target_hashes:
            found_time = time.time() - start_time
            target_hashes[md5_hash_hex] = (anagram, counter, found_time)
            remaining_targets.remove(md5_hash_hex)
            print("FOUND after {} sec:".format(found_time))
            print(md5_hash_hex, "->", "'" + anagram + "'")
    if len(remaining_targets) > 0:
        print(
            "Searched:", counter,
            "anagrams but did not find all. Try different number of spaces.")
        print("*" * 80)
        for key, value in target_hashes.items():
            print(key, "->", value)
            print("=" * 80)
    else:
        print("Found All targets!")


def load_task(task_path: pathlib.Path) -> Tuple[str, Dict]:
    anagram = ""
    target_hashes = {}
    with open(task_path, "r") as f:
        first_line = f.readline()
        anagram = first_line.strip()
        for line in f:
            hash = line.strip()
            if not hash == "":
                target_hashes[hash] = None
    return (anagram, target_hashes)


def main():
    current_dir_path = pathlib.Path().resolve()
    task_path = current_dir_path.joinpath("task")

    anagram, target_hashes = load_task(task_path)
    print("Anagram: ", anagram),
    print("Target hashes:")
    for hash in target_hashes.keys():
        print(hash)
    number_of_spaces_in_anagram = anagram.count(" ")
    anagram_without_spaces = anagram.replace(" ", "")
    prompt_message = ("Anagram has {0} spaces. "
                      "How many spaces do you want? (default: {0}): "
                      ).format(number_of_spaces_in_anagram)
    usr_input = input(prompt_message)
    if usr_input == "":
        wanted_spaces = number_of_spaces_in_anagram
    elif usr_input.isdigit():
        wanted_spaces = int(usr_input)
    else:
        raise ValueError(
            "Number of spaces must be a digit. You wrote '{}'.".format(
                usr_input))

    only_ascii = False
    only_alpha = False
    anagram_len = len(anagram_without_spaces)
    if anagram_without_spaces.isascii():
        only_ascii = True
    if anagram_without_spaces.isalpha():
        only_alpha = True
    wordlist_path = current_dir_path.joinpath("wordlist")

    word_dict = load_word_dict(wordlist_path, anagram_len, only_ascii,
                               only_alpha)
    word_dict = remove_impossible_words(word_dict, anagram_without_spaces)
    wordlist_trie = trie.Trie(list(word_dict.keys()))

    anagrams_queue = mp.Manager().Queue()
    anagram_process_args = (anagram_without_spaces, wanted_spaces,
                            anagrams_queue)
    anagrams_process = mp.Process(target=wordlist_trie.anagrams,
                                  args=anagram_process_args)
    check_hash_args = (anagrams_queue, target_hashes)
    check_hash_process = mp.Process(target=check_hash, args=check_hash_args)
    anagrams_process.start()
    check_hash_process.start()
    print("Search started.")
    check_hash_process.join()
    if anagrams_process.is_alive():
        anagrams_process.terminate()


if __name__ == "__main__":
    main()