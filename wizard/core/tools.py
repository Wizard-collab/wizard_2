# condig: utf-8

# Python modules
import hashlib, binascii
import os
import re

def encrypt_string(string):
    """Hash a string for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', string.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def decrypt_string(stored_string, provided_string):
    """Verify a stored password against one provided by user"""
    salt = stored_string[:64]
    stored_string = stored_string[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_string.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_string

def is_safe(input):
    charRe = re.compile(r'[^a-zA-Z0-9._]')
    string = charRe.search(input)
    return not bool(string)
