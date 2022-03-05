# trustpilot_md5

## Requirements
- Python3.9 or higher. I used PyPy3.9 for its speed.

## Ideas

1. Understand the problem.
1. Think about how to reduce the search space.
1. Think if spaces are part of the solution. If yes then how many?
1. Think about what data structures can help.
1. CPython is slow. Use JIT compiler. [PyPy3](https://www.pypy.org/)


## Steps for solving the challenge.

1. Load the wordlist and remove potential duplicate words.
1. Keep only words that can be part of the anagram. This reduced the number of words from 99 175 to 1659 words.
1. Use Trie structure to store the 1659 words. This allows for efficient anagrams generation. For more details see "The Algorithm Design Manual", 3rd Edition by Steven Skiena page 448.
1. Check for hash collision against the target hashes.

# Example

- Run with this command (CPython): `python3.9 main.py wordlist task --log INFO`. 
- Log is optional arg and values can be `[DEBUG | INFO | WARNING | ERROR | CRITICAL]` default is `WARNING`
- For PyPy3 run with this command: `pypy3.9 main.py wordlist task --log INFO`

# Result

See the [results.txt](results.txt) file