"""
Checks mnemonic phrases found by main.py for valid checksums, produces a list of these phrases.
Phrases are then converted to Base58(P2SH) i.e Segwit addresses.
The Blockcypher library is used to check if there have been past transactions on the accounts.
If you wish to use this module as a standalone to verify the validity of mnemonic phrases,
they must be passed in so: [[phrase],[phrase],...] where 'phrase' is ['word1','word2',...]
"""

import blockcypher
from bip32utils import BIP32Key
from bip32utils import BIP32_HARDEN
from btclib import bip39


def checksum_validator(lst_filtered_possibilities):
    """
    :param lst_filtered_possibilities: unique mnemonic phrases generated by main.py
    :return: list of mnemonic phrases with valid checksums according to BIP39 spec
    """
    checksum_valid = []
    print("\nValidating...")
    for mnemonic_phrase in lst_filtered_possibilities:
        try:  # BIP39 Filtering - checks whether the phrases produce a valid entropy according to BIP39.
            bip39.entropy_from_mnemonic(" ".join(mnemonic_phrase), "en")
            checksum_valid.append(mnemonic_phrase)
        except ValueError:  # Entropy was invalid
            pass
        except TypeError:
            pass
    print(f'\nFound {len(checksum_valid)} valid mnemonics.')
    return checksum_valid


def derive_address(list_of_mnemonics):
    """
    :param list_of_mnemonics: list of unique mnemonic phrases with valid checksums
    """
    addresses = {}
    print("\nDeriving addresses")
    for possibility in list_of_mnemonics:
        str_poss = ' '.join(possibility)
        seed = bip39.seed_from_mnemonic(str_poss, "")  # Converting mnemonic to BIP39 Seed
        key = BIP32Key.fromEntropy(seed)  # Converting to BIP32 Root Key
        account_number = 0  # This variable can be changed to attain a different derivation path
        i = 0  # This variable can be changed to attain a different derivation path
        # For the following account derivation `BIP32_HARDEN` can be simply removed to access unhardened addresses
        addr = (key.ChildKey(49 + BIP32_HARDEN)
                .ChildKey(0 + BIP32_HARDEN)
                .ChildKey(account_number + BIP32_HARDEN)
                .ChildKey(0)
                .ChildKey(i)
                .P2WPKHoP2SHAddress())
        addresses[addr] = str_poss

    print(f"\n{len(addresses)} addresses derived.")
    for address in addresses:
        print(f"Checking address {address}")
        if blockcypher.get_total_num_transactions(address) > 0:
            print(f'\nThe correct address is: {address}\nThe correct mnemonic is: \n{addresses[addr]}')
            quit()


if __name__ == "__main__":
    pass
