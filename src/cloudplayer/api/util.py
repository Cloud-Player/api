"""
    cloudplayer.api.util
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import math
import multiprocessing
import random
import string


def gen_token(n, alphabet=string.ascii_lowercase + string.digits):
    """Cryptographically sufficient token generator for length `n`."""
    urand = random.SystemRandom()
    return ''.join(urand.choice(alphabet) for i in range(n))


def chunk_range(size, min_step=10, chunks=multiprocessing.cpu_count()):
    """Evenly chunk a range of `size` into `chunks` with `min_step`."""
    size = max(size, 1)
    step = max(int(math.ceil(size / max(chunks, 1))), min_step)
    ranges = list(zip(range(0, size, step), range(step, size + step, step)))
    # Inject `None` as a slice operator to catch the last item
    ranges[-1] = (ranges[-1][0], None)
    return ranges


def squeeze(string):
    """Squeezes any whitespaces or linebreaks out of `string`."""
    return ''.join(string.split())
