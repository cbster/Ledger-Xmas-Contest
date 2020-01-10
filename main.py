"""
This script will take the hints and words from words_hints.py and derive from them a list of valid mnemonics that
fulfill the following criteria (in order of how they are sorted in this program):
1. The words in the mnemonic phrase are spelled correctly and exist in the BIP39 dictionary.
2. The mnemonic phrases are only represented once in the list of possibilities.
3. The mnemonic phrases do not repeat any words within themselves.
4. The mnemonic phrase, when converted to entropy, contains a valid checksum according to BIP39 spec.
"""

import concurrent.futures
import itertools
import time

from threading import Thread
import numpy

from checker import derive_address, checksum_validator
from words_hints import hints, mnemonic_words

with open("dictdata/english.txt", 'r') as bip_39_words:
    all_mnemonic_words = bip_39_words.read().split("\n")[:-1]


def mnemonic_valid_check(word_list):
    """Checks that the words from a given list are in the BIP39 dictionary in ../dictdata
    :param word_list: list of potential words in the mnemonic phrase
    """
    for words in word_list:
        if words not in all_mnemonic_words:
            print("Error! Mnemonic words are not valid.")
        else:
            pass


def construct_list_apc(hint_list, word_list):
    """Returns a list of lists containing the possible words that would fit into a given slot according to the hints
    :param word_list: list of potential words in the mnemonic phrase
    :param hint_list: list of hinted first letters (in order)
    :return: list of lists containing all possible words that would fit into a given slot according to the hint letters
    """
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
    """Used to calculate the number of possible combinations when words are not repeated within mnemonic phrase
    :param list_of_combinations: list of lists passed in from construct_list_apc containing words for each spot
    :return: list of values representing how many mnemonic words could be used in a given place
    """
    lst = []
    char_count = {word[0][0]: len(word) for word in list_of_combinations}
    for letter in hints:
        lst.append(char_count[letter])
        char_count[letter] -= 1
    return lst


def estimator(apc):
    """Provides an instant calculation of how many combinations are possible
    :param apc: list of all possible combinations generated by construct_list_apc
    """
    print(f'Total possible combinations (with repetitions): {numpy.prod([len(combos) for combos in apc])}')
    print(f'Total possible combinations (without repetitions): {numpy.prod(combination_count(apc))}')


def repetition_filter():
    """The most intensive part of the program. Ensures that there are no repeated words within the mnemonic phrase.
    If you wish to filter a list with a large amount of possible combinations (>5.000.000) you can change
    the list comprehension for `possibilities` below to a generator by changing the square brackets to parentheses
    :return: list of unique mnemonic phrases with no repeated words
    """
    possibilities = [item for item in itertools.product(*all_possible_combinations)]  # Produces a cartesian product

    def unique_filter(mnemonic_phrases):
        """Processes each possible mnemonic phrase to ensure that each word in the phrase is unique (docstring point 3)
        :param mnemonic_phrases: single mnemonic phrase passed in from list `possibilities` of all phrases
        :return: list of unique mnemonic phrases with no repeated words
        """

        def timer():
            """Run in a thread, provides a representation of progress during the filtering phase (it can take while)"""
            latest_filter_count = 0
            filter_start_time = time.time()
            while is_filtering:
                time.sleep(5)
                elapsed_time = time.time() - filter_start_time
                speed = (len(unique_items) - latest_filter_count) / 5
                time_remaining = (numpy.prod(combination_count(all_possible_combinations)) - len(unique_items)) / speed
                percentage = int((len(unique_items) / numpy.prod(combination_count(all_possible_combinations))) * 100)
                print(f"{len(unique_items)} found, {percentage}% scanned, {int(round(speed))} found per second "
                      f"(Elapsed: {int(round(elapsed_time))}s, Remaining: {int(round(time_remaining))}s)")
                latest_filter_count = len(unique_items)

        unique_items = []
        status = Thread(target=timer, daemon=True)
        is_filtering = True
        status.start()
        for individual_phrase in mnemonic_phrases:
            if len(individual_phrase) == len(set(individual_phrase)):
                unique_items.append(individual_phrase)
        is_filtering = False
        status.join()  # Timer function no longer required, filtering is complete
        return unique_items

    print("\nChecking for unique phrases (no repeated words)...")
    with concurrent.futures.ThreadPoolExecutor() as t_pool:  # Executes the filtering process across multiple threads
        result = t_pool.submit(unique_filter, possibilities)
        return result.result()


if __name__ == "__main__":
    mnemonic_valid_check(mnemonic_words)
    all_possible_combinations = construct_list_apc(hints, mnemonic_words)
    estimator(all_possible_combinations)

    # From here, the search for the mnemonic phrases themselves begins
    possibilities_filtered = repetition_filter()
    print(f"\n{len(possibilities_filtered)} unique phrases found. These will have their checksums validated.")
    valid_mnemonics = checksum_validator(possibilities_filtered)

    # Finally, addresses are derived from the valid mnemonics and are checked for transaction count > 0
    derive_address(valid_mnemonics)
