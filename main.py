"""
This script will take the hints and words from words_hints.py and derive from them a list of valid mnemonics that
fulfill the following criteria (in order of how they are sorted in this program):
1. The words in the mnemonic phrase are spelled correctly and exist in the BIP39 dictionary.
2. The mnemonic phrases are only represented once in the list of possibilities.
3. The mnemonic phrases do not repeat any words within themselves.
4. The mnemonic phrase, when converted to entropy, contains a valid checksum according to BIP39 spec.
"""

import itertools
import json
import time
from threading import Thread

import numpy
from btclib import bip39

from words_hints import hints, mnemonics

with open("dictdata/english.txt", 'r') as bip_39_words:
    all_mnemonic_words = bip_39_words.read().split("\n")[:-1]


def mnemonic_valid_check(word_list):
    """Checks that the words from a given list are in the BIP39 dictionary in ../dictdata"""
    for words in word_list:
        if words not in all_mnemonic_words:
            print("Error! Mnemonic words are not valid.")
        else:
            pass


def words_starting_with(word_list):
    """Creates a dictionary containing a letter as key
    and how many times a word begins with that letter in the given list as its value"""
    word_chars = {}
    for word in word_list:
        word_first_char = word[0]
        if word_first_char not in word_chars:
            word_chars[word_first_char] = 0
        word_chars[word_first_char] += 1
    return word_chars


def hints_starting_with(hint_list):
    """Creates a dictionary containing a letter as key
    and how many times a hint begins with that letter in the given list as its value"""
    hint_chars = {}
    for hint_char in hint_list:
        if hint_char != "":
            hint_chars[hint_char] = 0
        hint_chars[hint_char] += 1
    return hint_chars


def construct_list_apc(hint_list, word_list):
    """Returns a list of lists containing the possible words that would fit into a given slot according to the hints"""
    all_possible_combos = []
    for char in hint_list:
        if len(char) == 1:
            combos = []
            for word in word_list:
                if word[0] == char:
                    combos.append(word)
            all_possible_combos.append(combos)
    return all_possible_combos


def combination_count(list_of_combinations):
    """Used to calculate the number of possible combinations when words are not repeated within mnemonic phrase"""
    lst = []
    char_count = {word[0][0]: len(word) for word in list_of_combinations}
    for letter in hints:
        lst.append(char_count[letter])
        char_count[letter] -= 1
    return lst


def timer():
    """Run in a thread, provides a representation of progress during the filtering phase."""
    latest_filter_count = 0
    filter_start_time = time.time()
    while is_filtering:
        time.sleep(5)
        elapsed_time = time.time() - filter_start_time
        speed = (filter_count - latest_filter_count) / 5
        time_remaining = (unfiltered_possible_combos - filter_count) / speed
        percentage = int((filter_count / unfiltered_possible_combos) * 100)
        print(f"{len(possibilities_filtered)} found, {percentage}% scanned, {int(round(speed / 1000))}k/s "
              f"(Elapsed: {int(round(elapsed_time))}s, Remaining: {int(round(time_remaining))}s)")
        latest_filter_count = filter_count


mnemonic_valid_check(mnemonics)
all_possible_combinations = construct_list_apc(hints, mnemonics)
# The below section provides an instant calculation of how many combinations are possible
unfiltered_possible_combos = numpy.prod([len(combos) for combos in all_possible_combinations])
total_possible_combos = numpy.prod(combination_count(all_possible_combinations))
print(f'Total possible combinations (with repetitions): {unfiltered_possible_combos}')
print(f'Total possible combinations (without repetitions): {total_possible_combos}')
# From here, the search for the combinations themselves begins
possibilities = itertools.product(*all_possible_combinations)  # Produces a cartesian product
print("\nChecking for unique phrases (no repeated words)...")

possibilities_filtered = []
is_filtering = True
filter_count = 0

status = Thread(target=timer)  # Sets the thread that will display filtering progress
status.start()
for possibility in possibilities:
    if len(possibility) == len(set(possibility)):  # Sets must have unique items (see point 3 in docstring)
        possibilities_filtered.append(possibility)
    filter_count += 1
is_filtering = False
status.join()  # Status thread is no longer required
print(f"\n{len(possibilities_filtered)} unique phrases found. These will have their checksums validated.")

valid_mnemonics = []
print("\nValidating...")
for mnemonic_phrase in possibilities_filtered:
    try:  # BIP39 Filtering - checks whether the phrases produce a valid entropy according to BIP39.
        bip39.entropy_from_mnemonic(" ".join(mnemonic_phrase), "en")
        valid_mnemonics.append(mnemonic_phrase)
    except ValueError:  # Entropy was invalid
        pass

with open("valid_possibilities.out.txt", "w") as f:  # Write BIP-39 valid mnemonics to JSON for checker.py
    f.write(json.dumps(valid_mnemonics))

print(f'\nFound {len(valid_mnemonics)} valid mnemonics.')
