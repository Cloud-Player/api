"""
    cloudplayer.api.util
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import random
import string


def gen_token(n, alphabet=string.ascii_lowercase + string.digits):
    urand = random.SystemRandom()
    return ''.join(urand.choice(alphabet) for i in range(n))
