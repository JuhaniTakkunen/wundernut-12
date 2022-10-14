import pytesseract
from PIL import Image


def extract_character_from_image(img: Image.Image, tesseract_exe=None):
    """OCR scan an image and return a single character.

    Unfortunately using Tesseract was not as easy as I was hoping, and
    I was not able to successfully recognize capital I with PSM-10.
    Therefore, there is a default that if the scan fails, we assume that the
    character is I. This does not make me happy, but it works in _this_ case.

    Future improvements:
        - PSM-10 (single character) mode was used, because otherwise Tesseract
        does not work well with encrypted text. It might be that this is a
        configuration error, and other modes could also be used.
        - un-used config settings are left as comments, these might be important
        if other modes are used
        - creating language library with decrypted words might allow Tesseract
        to scan encrypted text as well.
    """
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe

    config = (
        "--oem 3 --psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # " load_system_dawg=false"
        # " load_freq_dawg=false"
        # " load_punc_dawg=false"
        # " load_number_dawg=false"
        # " load_unambig_dawg=false"
        # " load_bigram_dawg=false"
        # " load_fixed_length_dawgs=false"
    )
    foo = pytesseract.image_to_string(img, config=config)
    if not foo:
        # If scan fails, we default to capital I. One could add here more
        # elegant error handling as well
        foo = "I"
    return foo.strip()
