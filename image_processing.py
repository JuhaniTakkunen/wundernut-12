import logging
from typing import List, Tuple

import numpy as np
from PIL import ImageOps, ImageFilter, Image


logger = logging.getLogger(__name__)


def split_indexes(data, axis=1) -> List[Tuple[int, int]]:
    """Search for indexes where image can be split into sections

    Image is only split from sections where the background is white through
    entire image.

    Result is a list of tuples with two integers. Integers represent
    the start and stop of a non-white segment in the image (with padding).
    """
    white_count = data.shape[axis] * 255 * 3  #
    row_color_count = data.sum(axis=axis).sum(axis=1).tolist()
    rows_all_white = [x == white_count for x in row_color_count]

    text_block = False
    start_index = 0
    white_space = 5  # padding around non-white row
    res = []

    for row_index, row_whiteness in enumerate(rows_all_white):
        if not row_whiteness and not text_block:
            start_index = row_index - white_space
            if start_index < 0:
                start_index = 0
            text_block = True
        elif row_whiteness and text_block:
            stop_index = row_index + white_space

            if stop_index - start_index < 80:
                stop_index += 10
                start_index -= 10

            if start_index < 0:
                start_index = 0
            if stop_index > len(rows_all_white):
                stop_index = len(rows_all_white)

            text_block = (start_index, stop_index)
            res.append(text_block)

            text_block = False
            start_index = None

    if text_block:
        res.append((start_index, len(rows_all_white)))
    return res


def pre_process_image(
    img: Image.Image, save_files_for_debug=False
) -> List[Image.Image]:
    """Pre-prosess image for OCR-scan.

    This function:
        - transforms the image into black-and-white
            * Assumption: image only has two colors, and the dominating color
                          is the background
        - split image into smaller images with only one character
    """

    im = img.convert("RGBA")

    # --- STEP 1: image to black-and-white --- #
    colors = im.getcolors()

    background_color = max(colors)[1]
    max_red, max_green, max_blue = background_color[:3]

    text_color = min(colors)[1]
    min_red, min_green, min_blue = text_color[:3]

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Dominating color to white, "background"
    white_areas = (red == max_red) & (blue == max_blue) & (green == max_green)
    data[...][white_areas.T] = (255, 255, 255, 0)  # Transpose back needed

    # Secondary color to black, "text"
    black_areas = (red == min_red) & (blue == min_blue) & (green == min_green)
    data[...][black_areas.T] = (0, 0, 0, 0)  # Transpose back needed

    # --- STEP 2: split image --- #

    horizontal_indexes = split_indexes(data, axis=1)

    images = []
    for h_counter, (h_start, h_end) in enumerate(horizontal_indexes):
        sub_data = data[h_start:h_end]
        vertical_indexes = split_indexes(sub_data, axis=0)

        for v_counter, (v_start, v_end) in enumerate(vertical_indexes):
            subsub_data = sub_data[:, v_start:v_end]
            sub_image = Image.fromarray(subsub_data)

            # --- STEP 2b: enhance image --- #

            # convert greyscale
            sub_image = ImageOps.grayscale(sub_image)

            # increase resolution
            width, height = sub_image.size
            sub_image = sub_image.resize((width * 6, height * 6))

            # blur
            sub_image = sub_image.filter(ImageFilter.MedianFilter(21))

            # border
            sub_image = ImageOps.expand(sub_image, border=10, fill="black")

            file_path = f"images/foo_{h_counter}-{v_counter}.png"

            if save_files_for_debug:
                logger.info("Creating file for debugging: %s", file_path)
                sub_image.save(file_path)

            images.append(sub_image)

    return images
