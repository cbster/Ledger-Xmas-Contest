import json

from btclib import bip39
import numpy
import itertools
from words_hints import hints, mnemonics
import datetime

with open("dictdata/english.txt", 'r') as bip_39_words:
    all_mnemonic_words = bip_39_words.read().split("\n")[:-1]


def mnemonic_valid_check(word_list):
    for words in word_list:
        if words not in all_mnemonic_words:
            print("Error! Mnemonic words are not valid.")
        else:
            pass


def words_starting_with(word_list):
    word_chars = {}
    for word in word_list:
        word_first_char = word[0]
        if word_first_char not in word_chars:
            word_chars[word_first_char] = 0
        word_chars[word_first_char] += 1
    return word_chars


def hints_starting_with(hint_list):
    hint_chars = {}
    for hint_char in hint_list:
        if hint_char != "":
            hint_chars[hint_char] = 0
        hint_chars[hint_char] += 1
    print(hint_chars)
    return hint_chars


def construct_list_apc(hint_list, word_list):
    all_possible_combos = []
    for char in hint_list:
        if len(char) == 1:
            combos = []
            for word in word_list:
                if word[0] == char:
                    combos.append(word)
            all_possible_combos.append(combos)
    return all_possible_combos


def num_possible_combos(apc):
    return [len(combos) for combos in apc]


mnemonic_valid_check(mnemonics)
total_possible_combos = []
all_possible_combinations = construct_list_apc(hints, mnemonics)
npc = num_possible_combos(all_possible_combinations)
for x in npc:
    if x == 1:
        total_possible_combos.append(x)
    elif 1 < x:
        total_possible_combos.append(x - 1)
total_possible_combos = numpy.prod(total_possible_combos)
unfiltered_possible_combos = numpy.prod(num_possible_combos(construct_list_apc(hints, mnemonics)))
print(f'Total possible combinations (with repetitions): {unfiltered_possible_combos}')
print(f'Total possible combinations (without repetitions): {total_possible_combos}')
possibilities = itertools.product(*all_possible_combinations)
print("Filtering possibilities...")
possibilities_filtered = []
filter_count = 0
for possibility in possibilities:
    if len(possibility) == len(set(possibility)):  # sets must have unique items
        possibilities_filtered.append(possibility)
    filter_count += 1

valid_mnemonics = []
print("Validating...")
for mnemonic_phrase in possibilities_filtered:
    # BIP-39 Filtering
    try:
        bip39.entropy_from_mnemonic(" ".join(mnemonic_phrase), "en")
        valid_mnemonics.append(mnemonic_phrase)
        print(f"Found valid BIP39 - ({len(valid_mnemonics)}/{len(possibilities_filtered)})")
    except ValueError:
        pass

# Write BIP-39 valid mnemonics
with open("valid_possibilities.out.txt", "w") as f:
    f.write(json.dumps(valid_mnemonics))

print(f'Found {len(valid_mnemonics)} valid mnemonics.')
