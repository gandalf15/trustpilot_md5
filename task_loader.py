"""
This file holds a function for loading a task from a file.
"""
import pathlib


def load_task(task_path: pathlib.Path) -> tuple[str, dict[str, None]]:
    """
    Loads the task from a file. First line must be the anagram.
    The rest are target hashes.

    Args:
        task_path: A path to the file with the task.

    Returns: tuple[anagram, dict of target hashes]
    """
    target_hashes = {}
    with open(task_path, "r", encoding="utf-8") as task_file:
        first_line = task_file.readline()
        anagram = first_line.strip()
        for line in task_file:
            target_hash = line.strip()
            if not target_hash == "":
                target_hashes[target_hash] = None
    return (anagram, target_hashes)
