# Lab 11 — Decrypting the Intercepted Message

Secure Communications lab. The Gardaí recovered a partially damaged Python
encryption program from a suspect's machine, along with an intercepted
message. The task was to work out what the program did and recover the
plaintext.

## Result

```
Why do elephants have big ears?
```

The intercepted message was 35,138 characters long and held **68 layers** of
encoding.

## Files

| File | What it is |
|---|---|
| `encryptme.py` | The damaged program as supplied (Python 2, `&&&&` marks the missing parts) |
| `ciphertext.txt` | The intercepted message |
| `decryptme.py` | Our decoder — this is the one to run |
| `encryptme_py3.py` | The original repaired and ported to Python 3, used to generate test data |

## Running it

```bash
python3 decryptme.py -f ciphertext.txt
```

Other ways to call it:

```bash
python3 decryptme.py "2V2h5IGRvIGVsZXBoYW50cyBoYXZlIGJpZyBlYXJzPw=="   # inline
python3 decryptme.py                                                    # paste when prompted
python3 decryptme.py -f ciphertext.txt | tail -20                       # last few rounds only
python3 decryptme.py -f ciphertext.txt > result.txt                     # save the full trace
```

Needs nothing but a stock Python 3 — no packages to install.

## How the encryption worked

`encryptme.py` defines three transforms:

| Step | Transform | Reverse |
|---|---|---|
| `step1` | ROT13 — every letter moved 13 places | ROT13 again (it undoes itself) |
| `step2` | Base64 encode | Base64 decode |
| `step3` | Lowercase letters shifted forward 4 (`a`→`e`) | Shift back 4. Uppercase and digits are untouched |

`step1` looks obscure because the translation table is written out letter by
letter, but lining the two strings up shows `z`→`m`, `y`→`l` … `m`→`z`, which
is plain ROT13.

`make_secret` is where it gets interesting:

```python
a = '2{}'.format(b64encode(plain))
for count in xrange(count):
    r = random.choice(secret_encoding)   # pick one of the three at random
    si = secret_encoding.index(r) + 1    # 1, 2 or 3
    _a = globals()[r](a)                 # apply it
    a = '{}{}'.format(si, _a)            # write down which one was used
```

The message is base64 encoded once to start with, then wrapped in randomly
chosen transforms. Because the order is random, the program **records each
choice as a digit at the front of the string**.

That is the weakness. The random order is unknowable, but the program leaves
the full sequence sitting in the ciphertext where anyone can read it. The
leading digit always names the transform applied last.

## How we decrypted it

Read the first character, strip it, apply the matching reverse transform,
repeat:

| Leading digit | Action |
|---|---|
| `1` | ROT13 the rest |
| `2` | Base64 decode the rest |
| `3` | Shift lowercase back 4 |

Loop until the string no longer starts with `1`, `2` or `3`. The decoder also
stops if a reverse transform throws, which covers the case of a plaintext that
happens to begin with a digit.

The last rounds of the real message:

```
[65] undid step1 -> 112V2h5IGRvIGVsZXBoYW50cyBoYXZlIGJpZyBlYXJzPw==
[66] undid step1 -> 12I2u5VTEiVTIfMKObLJ50plObLKMyVTWcMlOyLKWmCj==
[67] undid step1 -> 2V2h5IGRvIGVsZXBoYW50cyBoYXZlIGJpZyBlYXJzPw==
[68] undid step2 -> Why do elephants have big ears?
```

## The damaged parts

```python
secret = '&&&&&&&&&&&&&&'    # the plaintext
print make_secret(secret, count=&&&)
```

Neither needed guessing:

- `secret` is the message we were asked to recover, so there was nothing to
  reconstruct.
- `count` is the number of rounds, and every round already tagged itself with
  its own digit. We just peel until there is nothing left to peel. It came to
  68.

## Python 2 vs Python 3

The original is Python 2 and will not run as-is on a current Kali. The changes
needed were:

| Python 2 | Python 3 |
|---|---|
| `string.maketrans(a, b)` | `str.maketrans(a, b)` |
| `string.translate(s, t)` | `s.translate(t)` |
| `xrange(n)` | `range(n)` |
| `print x` | `print(x)` |
| `b64encode(str)` | `b64encode(bytes)` — needs `.encode()` / `.decode()` |

The base64 one is the easy trap: in Python 3 base64 works on bytes rather than
strings, so every call has to convert on the way in and on the way back out.

## Checking our work

`encryptme_py3.py` is the repaired encoder. Running the same plaintext through
it and feeding the result back into `decryptme.py` returns the original string,
which confirms we read the original program correctly:

```bash
python3 encryptme_py3.py > test.txt
python3 decryptme.py -f test.txt | tail -3
```
