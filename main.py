#! /usr/bin/env python3
"""
Trustpilot coding challenge
"""

import argparse
import hashlib
import logging
import multiprocessing as mp
import pathlib
import time

import dict_loader
import task_loader
import trie

# Constants
# Name of the file where results will be appended.
RESULTS_FILE_NAME = "results.txt"


def check_hash(logger: logging.Logger, anagrams_queue: mp.Queue,
               target_hashes: dict[str:None]):
    """
    Check MD5 target_hashes against generated anagrams  MD5 hashes.
    If there is a match then it will print it and save it in a file.

    Args:
        logger: logger for logging.
        anagrams_queue: Queue with potential anagrams.
        target_hashes: Dict of target hashes to find.
    """
    counter = 0
    start_time = time.time()
    while len(target_hashes) > 0:
        anagram = anagrams_queue.get()
        anagrams_queue.task_done()
        if anagram is None:
            logger.info("No more anagrams in the Queue.")
            break
        # Get MD5 Hash of the anagram.
        md5_hash = hashlib.md5(anagram.encode('utf-8'))
        md5_hash_hex = md5_hash.hexdigest()

        counter += 1
        logger_message = [
            f"Checked: {counter} anagrams and searching. ",
            f"Current anagram: '{anagram}'"
        ]
        if counter % 1000 == 0:  # Info log message every 1000th anagram.
            logger.info("".join(logger_message))

        if md5_hash_hex in target_hashes:
            found_time = int(time.time() - start_time)
            del target_hashes[md5_hash_hex]
            message = (f"FOUND: Anagram number {counter} in {found_time} sec: "
                       f"{md5_hash_hex} -> '{anagram}'\n")
            print(message)
            with open(RESULTS_FILE_NAME, "a",
                      encoding="utf-8") as results_file:
                results_file.write(message)
        else:
            logger_message.append(f" -> MD5 Hash: '{md5_hash_hex}'.")
            logger.debug("".join(logger_message))

    if len(target_hashes) > 0:
        message = [f"Searched {counter} anagrams but did not find:"]
        message = message + list(target_hashes)
        message.append("Try different number of spaces.")
        print("\n".join(message))
    else:
        print("Found All target hashes!")
    print(f"Found hashes are in file '{RESULTS_FILE_NAME}'.")


def create_loggers(logger_names: tuple[str]) -> tuple[logging.Logger]:
    """
    Creates loggers with provided names.

    Args:
        logger_names: Names of loggers to create.

    Return: A tuple with created loggers.
    """
    # Create loggers.
    logging.basicConfig(format="%(asctime)s -> %(levelname)s: %(message)s")
    loggers = tuple(logging.getLogger(name) for name in logger_names)
    return loggers


def confirm_number_of_spaces(anagram: str) -> int:
    """
    Confirms with the user how many spaces should generated anagrams have.

    Args:
        anagram: Source anagram that is analised for number of spaces.

    Return: Number of spaces the user wants to have in generated anagrams.
    """
    number_of_spaces_in_anagram = anagram.count(" ")
    prompt_message = (f"Anagram has {number_of_spaces_in_anagram} spaces. "
                      "How many spaces should grenerated anagrams have?"
                      f"(default: {number_of_spaces_in_anagram}): ")
    usr_input = input(prompt_message)
    if usr_input == "":
        wanted_spaces = number_of_spaces_in_anagram
    elif usr_input.isdigit():
        wanted_spaces = int(usr_input)
    else:
        raise ValueError(
            f"Number of spaces must be a digit. You wrote '{usr_input}'.")
    return wanted_spaces


def solve_anagram(loggers: tuple[logging.Logger], wordlist_path: pathlib.Path,
                  task_path: pathlib.Path):
    """
    Solves anagram with a given word list and target MD5 hashes.
    It uses Trie structure to generate candidate anagrams.

    Args:
        loggers: Exactly 2 loggers for 2 processes.
        wordlist_path: A Path to a word dictionary. One word per line.
        task_path: A Path to a task. The first line is anagram and
            the rest are target hashes. One hash per line.
    """
    anagram, target_hashes = task_loader.load_task(task_path)

    logger_message = [f"\nAnagram: {anagram}"]
    logger_message.append("Target hashes: ")
    for target_hash in target_hashes:
        logger_message.append("\t" + target_hash)
    loggers[0].info("\n".join(logger_message))

    # Ask user how many spaces to include in the search.
    wanted_spaces = confirm_number_of_spaces(anagram)

    anagram_without_spaces = anagram.replace(" ", "")

    # Load words from file.
    word_dict = dict_loader.load_word_dict(wordlist_path,
                                           len(anagram_without_spaces),
                                           anagram_without_spaces.isascii(),
                                           anagram_without_spaces.isalpha())
    word_dict = dict_loader.remove_impossible_words(word_dict,
                                                    anagram_without_spaces)

    logger_message = f"Word dictionary contains {len(word_dict)} filtered words."
    loggers[0].info(logger_message)

    # Build a Trie structrure from filtered words.
    wordlist_trie = trie.Trie(list(word_dict.keys()))

    # Create process for generating anagrams from the Trie.
    anagrams_queue = mp.Manager().Queue()
    anagram_process_args = (anagram_without_spaces, wanted_spaces,
                            anagrams_queue)
    anagrams_process = mp.Process(target=wordlist_trie.anagrams,
                                  args=anagram_process_args)

    # Create process for checking hash collision.
    check_hash_args = (loggers[1], anagrams_queue, target_hashes)
    check_hash_process = mp.Process(target=check_hash, args=check_hash_args)

    # Start processes.
    anagrams_process.start()
    check_hash_process.start()

    print("Search started.")

    # Join check_hass process when it finishes. Either it found all hashes or
    # it exhausted the search space.
    check_hash_process.join()
    # Need to terminate anagrams_process when we found all hashes but did not
    # exhaust the search space.
    if anagrams_process.is_alive():
        anagrams_process.terminate()


def main() -> int:
    """
    Main function.
    """
    # Arguments
    parser = argparse.ArgumentParser(description="Trustpilot MD5 hash finder.")
    parser.add_argument("wordlist_path",
                        help="Path to the words dictionary file.")
    parser.add_argument("task_file_path", help="Path to the task file.")
    log_help_msg = ("Sets logging level (Default: WARNING)."
                    "[DEBUG | INFO | WARNING | ERROR | CRITICAL]")
    parser.add_argument("--log", help=log_help_msg, default="WARNING")
    args = parser.parse_args()

    loggers = create_loggers(("main", "check_hash"))

    # Set log level
    numeric_log_level = getattr(logging, args.log.upper(), None)
    if numeric_log_level is None:
        raise ValueError(f"Log level '{args.log}' is unknown.")
    for logger in loggers:
        logger.setLevel(numeric_log_level)

    wordlist_path = pathlib.Path(args.wordlist_path)
    task_path = pathlib.Path(args.task_file_path)
    solve_anagram(loggers, wordlist_path, task_path)

    return 0


if __name__ == "__main__":
    main()
