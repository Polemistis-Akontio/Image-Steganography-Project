# ImageDecoder.py
# Full decoding pipeline that reverses ImageEncoder.py

import cv2 as cv
import numpy as np
from numpy import binary_repr
from Crypto.Cipher import AES
import struct
import os
from hashlib import pbkdf2_hmac

def extract_binary_from_image(image_path: str, step_key: int) -> str:
    """Extracts LSB bits from image using the same step pattern as encoding."""
    img = cv.imread(image_path)
    assert img is not None, "Invalid image path"

    rows, cols, channels = img.shape
    total_vals = rows * cols * channels

    # Rebuild valueDict
    value_dict = {}
    count = 0
    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                value_dict[count] = (r, c, ch)
                count += 1

    # Rebuild steppedDict
    stepped_dict = {}
    key_list = list(value_dict.keys())
    visited = 0
    index = 0

    while visited < len(key_list):
        key = key_list[index % len(key_list)]
        if key not in stepped_dict:
            stepped_dict[key] = value_dict[key]
            index += step_key
            visited += 1
        else:
            break

    stepped_keys = list(stepped_dict.keys())

    # Extract LSB bits in the exact stored order
    bits = []
    for idx in stepped_keys:
        r, c, ch = stepped_dict[idx]
        bits.append(binary_repr(img[r, c, ch], 8)[7])

    return "".join(bits)


def decrypt_and_save(binary_string: str, password: str, output_file: str):
    """Reconstructs the encrypted blob, decrypts it using AES-GCM, and writes plaintext."""
    # Convert bitstring → bytes
    if len(binary_string) % 8 != 0:
        raise ValueError("Corrupted embedded data: bit length not multiple of 8")

    byte_array = bytearray()
    for i in range(0, len(binary_string), 8):
        byte_array.append(int(binary_string[i:i+8], 2))

    blob = bytes(byte_array)

    # Extract the structured fields
    salt = blob[:16]
    nonce = blob[16:32]
    tag = blob[32:48]
    header = blob[48:52]
    ciphertext_length = struct.unpack(">I", header)[0]

    ciphertext_start = 52
    ciphertext_end = 52 + ciphertext_length
    ciphertext = blob[ciphertext_start:ciphertext_end]

    # Re-derive AES key
    key32 = pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode(),
        salt=salt,
        iterations=100_000,
        dklen=32
    )

    cipher = AES.new(key32, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    # Write the restored file
    with open(output_file, "wb") as f:
        f.write(plaintext)

    print(f"Decrypted file saved as: {output_file}")


def decode_image():
    """Convenience wrapper: loads stepKey from savedInfo.txt and performs full decode."""
    if not os.path.exists("savedInfo.txt"):
        raise FileNotFoundError("savedInfo.txt missing — required for step key.")

    # Load step key
    with open("savedInfo.txt", "r") as f:
        lines = f.readlines()

    step_key = int(lines[0].split(":")[1].strip())
    image_file = lines[1].split(":")[1].strip()

    password = input("Enter decryption password: ")

    print("Extracting embedded bits...")
    bitstring = extract_binary_from_image(image_file, step_key)

    print("Decrypting data...")
    decrypt_and_save(bitstring, password, "DECODED_OUTPUT.bin")


if __name__ == "__main__":
    decode_image()