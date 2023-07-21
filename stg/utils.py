# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ..steganography.steganography.steganography import Steganography
import os, random, string


async def encode(path, output_path, text):
    Steganography.encode(path, output_path, text)


async def decode(path):
    secret_text = Steganography.decode(path)
    return secret_text


async def rename(filename, path):
    _, file_extension = os.path.splitext(filename)
    new_name = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(10)
    )
    os.rename(f"{path}/{filename}", f"{path}/{new_name}{file_extension}")
    return f"{new_name}{file_extension}"


async def get_text_from_file(filename):
    with open(filename, "r") as f:
        return f.read()


async def write_text_to_file(filename, text):
    with open(filename, "w") as f:
        f.write(text)


if __name__ == "__main__":
    # hide text to image
    path = f"{os.getcwd()}/stg/input.jpg"
    output_path = f"{os.getcwd()}/stg/output.jpg"
    text = "The quick brown fox jumps over the lazy dog."
    Steganography.encode(path, output_path, text)

    # read secret text from image
    secret_text = Steganography.decode(output_path)
    print(secret_text)
    os.remove(output_path)
    os.remove(path)
