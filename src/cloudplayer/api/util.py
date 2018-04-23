"""
    cloudplayer.api.util
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import random
import string


def gen_token(n, alphabet=string.ascii_lowercase + string.digits):
    """Cryptographically sufficient token generator for length `n`."""
    urand = random.SystemRandom()
    return ''.join(urand.choice(alphabet) for i in range(n))


def chunk_range(size, splits):
    """Evenly chunk a range of `size` into given number of `splits`."""
    step = int(size / splits)
    ranges = list(zip(range(0, size, step), range(step - 1, size, step)))
    ranges[-1] = (ranges[-1][0], None)
    return ranges
