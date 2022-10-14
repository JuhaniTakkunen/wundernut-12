import gzip
import logging
import re
import string
from io import BytesIO
from pathlib import Path
from typing import List, Literal

import requests
import wordninja
from english_words import english_words_lower_alpha_set


logger = logging.getLogger(__name__)


def get_list_of_spells(write_cache=False, force_cache=False) -> List[str]:
    """It seems that the secret message might contain English spells. This
    function retrieves list of spells from Finnish Harry Potter wiki.

    If the web-connection is not working for any reason, as a backup the
    function can use cached result in spells.txt
    """
    source_url = "http://fi.harrypotter.shoutwiki.com/wiki/Luettelo_loitsuista"
    try:
        if force_cache:
            raise ConnectionError("Force cache")
        response = requests.get(source_url)
        regex_pattern = "\(\s*<i>eng\. (.*)<\/i>\s*\)"  # english spells
        result_list = re.findall(regex_pattern, response.text)
    except Exception:
        logger.exception("Getting spells from %s failed", source_url)
        logger.info("Using cache instead...")
        result_list = Path("spells.txt").read_text("utf8").splitlines()

    if write_cache:
        spell_str = "\n".join(get_list_of_spells())
        Path("spells.txt").write_text(spell_str, "utf8")

    return result_list


def shift_string(my_string: str, shift: int):
    """Shift strings by index.

    Feature is documented in:
    https://stackoverflow.com/questions/40260555/how-to-shift-characters-according-to-ascii-order-using-python
    """
    alph_string = string.ascii_uppercase  # string of both uppercase/lowercase letters

    result = ""
    for character in my_string:
        if character in alph_string:
            new_index = ord(character) + shift
            if new_index > ord(alph_string[-1]):
                new_index -= len(alph_string)
            result += chr(new_index)
        else:
            result += "?"  # Default if character is unrecognized
    return result


def caesar_cipher_decrypt(encrypted_text: str) -> str:
    """Decrypt encrypted message automatically with brute-force.
    Use English alphabet (26 letters from A to Z)
    This is done by trying all combinations and returning the combo
    that has the greatest number of  recognized English words.
    """

    decrypted_texts = {}
    encrypted_text = encrypted_text.upper()
    for shift_amount in range(26):
        new_text = shift_string(encrypted_text, shift_amount)
        decrypted_texts[shift_amount] = new_text.lower()

    wordcount_per_shift = {}
    for shift_amount, text in decrypted_texts.items():
        words_found = 0
        for word in english_words_lower_alpha_set:
            if word in text:
                words_found += 1
        wordcount_per_shift[shift_amount] = words_found

    max_index = max(wordcount_per_shift, key=wordcount_per_shift.get)
    most_likely_row = decrypted_texts[max_index]

    return most_likely_row.upper()


def split_words(text, spell_method: Literal["A", "B"] = "B"):
    """Encrypted message does not have spaces between words.
    There are two methods for adding spaces (A and B).

    Both methods rely on Zipf's law (http://stackoverflow.com/a/11642687/2449774)
    and adds common spells to the process.

    Method A adds the spells to the word library used by wordninja
    (which is the library used for splitting string using Zipf's law).

    Method B first splits the words using common English words only,
    and then combines the spells if they were split up while doing splitting.

    Method B proved to be more reliable and therefore is the default. However,
    this might be an isolated case, and method A might work better generally.

    """
    text = text.lower()
    spell_words = get_list_of_spells()

    if spell_method == "A":
        word_file = (
            Path(wordninja.__file__).parent / "wordninja" / "wordninja_words.txt.gz"
        )

        with gzip.open(word_file, "rb") as zip_ref:
            res = zip_ref.read()

        res = res.decode("utf8")

        res += "\n".join(spell_words) + "\n"
        with BytesIO() as stream:
            with gzip.open(stream, "wb") as zip_ref:
                zip_ref.write(res.encode("utf8"))
            stream.seek(0)
            lang_model = wordninja.LanguageModel(stream)
            res = lang_model.split(text)
            res = " ".join(res)
    elif spell_method == "B":
        res = wordninja.split(text)
        res = " ".join(res)

        for spell in spell_words:
            spell = spell.lower()
            regex = r"\s" + r"\s?".join(spell) + r"\s"
            res = re.sub(regex, f" {spell} ", res)
    else:
        raise ValueError("Invalid spell method: %s", spell_method)

    return res.upper()


def decrypt_text(encrypted_message: str) -> str:
    """Decrypt encrypted message automatically, using Caesar Cipher and
    common English words. Add also spaces to the encrypted message as needed.
    """
    decrypted = caesar_cipher_decrypt(encrypted_message)
    final_text = split_words(decrypted)
    return final_text
