#!/usr/bin/env python3
"""
decryptme.py - reverses the encoding done by encryptme.py

The original program wrapped the message in a random sequence of three
transforms, and recorded which one it used by prepending its number:

    step1 = ROT13            (self-inverse)
    step2 = base64 encode    (reverse: base64 decode)
    step3 = shift lowercase forward 4   (reverse: shift back 4)

So the leading digit of the ciphertext tells us the LAST transform applied.
We peel the digits off one at a time, undoing each transform, until we are
left with readable text.

Usage:
    python3 decryptme.py "<ciphertext>"
    python3 decryptme.py -f message.txt
    python3 decryptme.py                  (then paste and press Enter)
"""

import sys
import string
from base64 import b64decode

# step1: ROT13 - applying it twice returns the original, so it is its own inverse
ROT13 = str.maketrans(
    "zyxwvutsrqponZYXWVUTSRQPONmlkjihgfedcbaMLKJIHGFEDCBA",
    "mlkjihgfedcbaMLKJIHGFEDCBAzyxwvutsrqponZYXWVUTSRQPON")

# step3: the encoder shifted lowercase letters forward 4 (a->e), so we shift back
low = string.ascii_lowercase
UNSHIFT4 = str.maketrans(low[4:] + low[:4], low)


def undo_step1(s):
    return s.translate(ROT13)


def undo_step2(s):
    return b64decode(s.encode()).decode()


def undo_step3(s):
    return s.translate(UNSHIFT4)


UNDO = {'1': undo_step1, '2': undo_step2, '3': undo_step3}


def decrypt(ciphertext, verbose=True):
    s = ciphertext.strip()
    round_no = 0

    while s and s[0] in UNDO:
        tag, rest = s[0], s[1:]
        try:
            nxt = UNDO[tag](rest)
        except Exception:
            # the leading digit was part of the message, not a step marker
            break
        round_no += 1
        s = nxt
        if verbose:
            preview = s if len(s) <= 70 else s[:70] + '...'
            print(f"  [{round_no:>2}] undid step{tag} -> {preview}")

    if verbose:
        print(f"\n  {round_no} transform(s) reversed\n")
    return s


def main():
    args = sys.argv[1:]

    if args and args[0] == '-f':
        with open(args[1]) as fh:
            ciphertext = fh.read()
    elif args:
        ciphertext = args[0]
    else:
        print("Paste the intercepted message, then press Enter:")
        ciphertext = sys.stdin.readline()

    ciphertext = ciphertext.strip()
    if not ciphertext:
        print("No ciphertext given.")
        return 1

    print(f"\nCiphertext ({len(ciphertext)} chars):\n  {ciphertext[:70]}"
          f"{'...' if len(ciphertext) > 70 else ''}\n")
    print("Peeling off the transforms:")

    plaintext = decrypt(ciphertext)

    print("=" * 60)
    print("DECODED MESSAGE:")
    print(plaintext)
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
