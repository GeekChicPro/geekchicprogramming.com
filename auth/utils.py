import random
import string

def generate_password(length=7):
    passwd = [random.choice(string.letters) for x in xrange(0, length+1)]
    return "".join(passwd)