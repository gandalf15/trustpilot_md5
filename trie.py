"""
This file hold Trie Class
"""
from typing import List, Dict


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

    def anagrams(self, string: str, max_spaces: int):
        result = []
        self._anagrams_helper(string, "", max_spaces, self.root, result)
        return result

    def _anagrams_helper(self, string: str, prefix: str, remaining_spaces: int,
                         node: Dict, result: List[str]) -> None:
        if not string:
            if self.end_symbol in node:
                result.append(prefix)
            return

        for node_letter, child in node.items():
            if node_letter in string:
                new_string = string.replace(node_letter, "", 1)
                new_prefix = prefix + node_letter
                self._anagrams_helper(new_string, new_prefix, remaining_spaces,
                                      child, result)

        if self.end_symbol in node and remaining_spaces > 0:
            remaining_spaces -= 1
            prefix += " "
            self._anagrams_helper(string, prefix, remaining_spaces, self.root,
                                  result)

    def __repr__(self) -> str:
        return str(self.root)
