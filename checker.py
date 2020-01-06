"""
This program will take the JSON full of mnemonic phrases written by main.py.
These are then converted to Base58(P2SH) i.e Segwit addresses.
The Blockcypher library is used to check if there have been past transactions on the accounts.
"""
import json

import blockcypher
from bip32utils import BIP32Key
from bip32utils import BIP32_HARDEN
from btclib import bip39

with open("valid_possibilities.out.txt", 'r') as possibilities:  # Reading in JSON written by main.py
    all_possibilities = json.loads(possibilities.read())
addresses = {}
print("Deriving addresses")
for possibility in all_possibilities:
    str_poss = ' '.join(possibility)
    seed = bip39.seed_from_mnemonic(str_poss, "")  # Converting mnemonic to BIP39 Seed
    key = BIP32Key.fromEntropy(seed)  # Converting to BIP32 Root Key
    account_number = 0  # This variable can be changed to attain a different derivation path
    i = 0               # This variable can be changed to attain a different derivation path
    # For the following account derivation, `BIP32_HARDEN` can be simply removed to access unhardened addresses
    addr = key.ChildKey(49 + BIP32_HARDEN) \
        .ChildKey(0 + BIP32_HARDEN) \
        .ChildKey(account_number + BIP32_HARDEN) \
        .ChildKey(0) \
        .ChildKey(i) \
        .P2WPKHoP2SHAddress()
    addresses[addr] = str_poss

print(f"{len(addresses)} addresses derived.")
for address in addresses:
    print(f"Checking address {address}")
    if blockcypher.get_total_num_transactions(address) > 0:
        print(f'The correct address is {address}\nThe correct mnemonic is: \n{addresses[addr]}')
        quit()
