"""
This file hold Trie Class
"""
import multiprocessing
from typing import List, Dict
import queue


class Trie:

    def __init__(self, wordlist: List[str]) -> None:
        self.root = {}
        self.end_symbol = "*"
        self.populate_trie_from(wordlist)

    def populate_trie_from(self, wordlist: List[str]) -> None:
        for word in wordlist:
            self.add_word(word)

    def add_word(self, word: str):
        node = self.root
        for letter in word:
            if letter not in node:
                node[letter] = {}
            node = node[letter]
        node[self.end_symbol] = True

    def anagrams(self, string: str, max_spaces: int,
                 results_queue: multiprocessing.Queue) -> None:
        self._anagrams_helper(string, "", max_spaces, self.root, results_queue)
        results_queue.put(None)

    def _anagrams_helper(self, string: str, prefix: str, remaining_spaces: int,
                         node: Dict,
                         results_queue: multiprocessing.Queue) -> None:
        if not string and remaining_spaces == 0:
            if self.end_symbol in node:
                results_queue.put(prefix)
            return

        for node_letter, child in node.items():
            if node_letter in string:
                new_string = string.replace(node_letter, "", 1)
                new_prefix = prefix + node_letter
                self._anagrams_helper(new_string, new_prefix, remaining_spaces,
                                      child, results_queue)

        if self.end_symbol in node and remaining_spaces > 0:
            remaining_spaces -= 1
            prefix += " "
            self._anagrams_helper(string, prefix, remaining_spaces, self.root,
                                  results_queue)

    def __repr__(self) -> str:
        return str(self.root)
