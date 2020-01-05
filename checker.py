import json

import blockcypher
from bip32utils import BIP32Key
from bip32utils import BIP32_HARDEN
from btclib import bip39

with open("valid_possibilities.out.txt", 'r') as possibilities:
    all_possibilities = json.loads(possibilities.read())
addresses = {}

print("Checking possibilities...")
for possibility in all_possibilities:
    str_poss = ' '.join(possibility)
    seed = bip39.seed_from_mnemonic(str_poss, "")
    key = BIP32Key.fromEntropy(seed)
    account_number = 0
    i = 0
    addr = key.ChildKey(49 + BIP32_HARDEN) \
        .ChildKey(0 + BIP32_HARDEN) \
        .ChildKey(account_number + BIP32_HARDEN) \
        .ChildKey(0) \
        .ChildKey(i) \
        .P2WPKHoP2SHAddress()
    addresses[addr] = str_poss

for address in addresses:
    if blockcypher.get_total_num_transactions(address) > 0:
        print(f'The correct address is {address} with mnemonic: {addresses[addr]}')
        quit()
