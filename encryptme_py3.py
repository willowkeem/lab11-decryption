#!/usr/bin/env python3
"""
encryptme_py3.py - the original encryptme.py, repaired and ported to Python 3.

Not needed to solve the lab, but it documents our reading of the damaged
original and lets us regenerate test ciphertexts to prove the decoder works.

What was damaged in the original, and how we handled it:

  secret = '&&&&&&&&&&&&&&'   the plaintext - this is what we were asked to
                              recover, so there was nothing to guess
  count  = &&&                the number of rounds - we did NOT need to guess
                              it either, because every round records its own
                              step number at the front of the string.  The
                              intercepted message turned out to hold 68 rounds.

Python 2 -> 3 changes required:
  string.maketrans(a, b)  ->  str.maketrans(a, b)
  string.translate(s, t)  ->  s.translate(t)
  xrange                  ->  range
  print x                 ->  print(x)
  b64encode works on bytes, not str, so .encode() / .decode() were added
"""

import string
import random
from base64 import b64encode

# step1: ROT13.  The original spelled the table out by hand; it maps
# z->m, y->l ... m->z, i.e. every letter moved 13 places.
ROT13 = str.maketrans(
    "zyxwvutsrqponZYXWVUTSRQPONmlkjihgfedcbaMLKJIHGFEDCBA",
    "mlkjihgfedcbaMLKJIHGFEDCBAzyxwvutsrqponZYXWVUTSRQPON")

# step3: lowercase letters only, shifted forward 4 places (a->e, b->f ...)
low = string.ascii_lowercase
SHIFT4 = str.maketrans(low, low[4:] + low[:4])


def step1(s):
    return s.translate(ROT13)


def step2(s):
    return b64encode(s.encode()).decode()


def step3(s, shift=4):
    return s.translate(SHIFT4)


secret_encoding = ['step1', 'step2', 'step3']


def make_secret(plain, count):
    # the message starts out base64 encoded, tagged with a leading '2'
    a = '2{}'.format(b64encode(plain.encode()).decode())

    for _ in range(count):
        r  = random.choice(secret_encoding)   # pick one of the three at random
        si = secret_encoding.index(r) + 1     # 1, 2 or 3
        a  = globals()[r](a)                  # apply it
        a  = '{}{}'.format(si, a)             # record which one we used

    return a


if __name__ == '__main__':
    secret = 'Why do elephants have big ears?'
    print(make_secret(secret, count=68))
