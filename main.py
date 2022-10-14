"""Author: Juhani Takkunen

This is a solution to a Wundernut-12 code-challenge:
https://github.com/wunderdogsw/wundernut-vol12

Solve the parchment mystery!

A blank parchment was found in the halls of Wunderwarts recently. The parchment
is believed to contain secret spells (in English) written with invisible ink.
They are probably encrypted. No known spells seem to work to decrypt it. We
need your help to solve this mystery!

Can you write some code to translate the hidden and encrypted text back to
muggle-readable form?

Parchment
Instructions & requirements

    Picture of the parchment can be found here.
    Choose any programming language and set of libraries for the task.
    The program needs to be able to handle the image, in order for the invisible
        ink text to become visible.
    The program must decrypt the text.
    The text must be printed in muggle-readable text format.
    The deadline to submit your solution is Sunday, September 25th.
    You get an extra point if you find out who might have written this parchment.

"""
import logging
from pathlib import Path

from PIL import Image

import decrypt_message
import image_processing
from ocr import extract_character_from_image

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_EXE = None


def main(image_path: Path):
    logger.info("Start processing image: %s", image_path)
    img = Image.open(image_path)
    sub_images = image_processing.pre_process_image(img)

    logger.info("Extract character from sub-images")
    extracted_text = ""
    for count, image in enumerate(sub_images):
        logger.info("Processing image: %s/%s", count, len(sub_images))
        character = extract_character_from_image(image, tesseract_exe=TESSERACT_EXE)

        logger.debug("...character: %s", character)
        extracted_text += character

    final_text = decrypt_message.decrypt_text(encrypted_message=extracted_text)
    final_text = final_text
    logger.info("Final result: %s", final_text)
    print("Result: ", final_text)
    print("Result without spaces: ", final_text.replace(" ", ""))
    return final_text


if __name__ == "__main__":
    main(image_path=Path(__file__).parent / "parchment.png")
