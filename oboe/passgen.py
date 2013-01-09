#passgen.py

from random import choice
import string

def generate_password(n):
    newpasswd = ''
    chars = string.letters + string.digits
    for i in range(n):
        newpasswd = newpasswd + choice(chars)
    return newpasswd
