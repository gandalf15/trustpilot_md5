"""
This file hold Trie class.
"""

import multiprocessing as mp

# define Node type
# See ptoblem with forward declaration:
# https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
Node = dict[str, "Node"]


class Trie:
    """
    Trie represents a trie data structure.

    Trie is an efficient information reTrieval data structure. Using Trie,
    search complexities can be brought to optimal limit (key length).
    However, Trie can be also used for efficient anagram generation.
    For more details see "The Algorithm Design Manual", 3rd Edition
    by Steven Skiena page 448.
    """

    def __init__(self, wordlist: list[str]) -> None:
        """
        Init a new instance of a Trie.

        Args:
            wordlist: List of words to store.
        """
        self._root = {}  # Node is a simple dict.
        self._end_symbol = "*"  # Word terminating character.
        self._populate_trie_from(wordlist)

    def _populate_trie_from(self, wordlist: list[str]) -> None:
        """
        Populates the trie from wordlist.

        Args:
            wordlist: List of words to store.
        """
        for word in wordlist:
            self.add_word(word)

    def add_word(self, word: str):
        """
        Adds one word to the trie.

        Args:
            word: The word to add.
        """
        node = self._root
        for letter in word:
            if letter not in node:
                node[letter] = {}
            node = node[letter]
        node[self._end_symbol] = True

    def anagrams(self, letters: str, spaces: int,
                 results_queue: mp.Queue) -> None:
        """
        Generates anagrams from given letters that exist in the trie.

        Args:
        letters: Letters for anagrams.
        spaces: Number of spaces that the generated anagram should have.
        results_queue: A queue where the generated anagrams are put.
            After all anagrams are generated, it puts None in the queue
            to signalise that it has finished.
        """
        self._anagrams_helper(letters, "", spaces, self._root, results_queue)
        results_queue.put(None)

    def _anagrams_helper(self, string: str, prefix: str, remaining_spaces: int,
                         node: Node, results_queue: mp.Queue) -> None:
        # Base case when we exhausted all the letters and spaces.
        # We have desired anagram.
        if not string and remaining_spaces == 0:
            if self._end_symbol in node:
                results_queue.put(prefix)
            return
        # Depth First Search for all valid anagrams.
        for child_letter, child_node in node.items():
            if child_letter in string:
                new_string = string.replace(child_letter, "", 1)
                new_prefix = prefix + child_letter
                self._anagrams_helper(new_string, new_prefix, remaining_spaces,
                                      child_node, results_queue)
        # We have a valid word but we still have some spaces to use.
        if self._end_symbol in node and remaining_spaces > 0:
            remaining_spaces -= 1
            prefix += " "
            self._anagrams_helper(string, prefix, remaining_spaces, self._root,
                                  results_queue)
