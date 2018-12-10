"""
Kryptoflask OpenSSL System Calls


"""

import os
import sys
import json
import datetime
import asyncio
import logging
import subprocess
import time
import kryptoflask

from time import sleep
from threading import Thread
from flask import Flask, redirect, url_for, request, render_template
from werkzeug import secure_filename

from . import openssl

UPLOAD_FOLDER = os.getcwd() + '/uploads'

def generate_key( bytes, base64=None):
    key_dir=os.path.join(UPLOAD_FOLDER, "key-file.txt")
    
    key_file = open(key_dir, 'w+')
    if base64 is None:

        print(base64, file=sys.stderr)
        p = subprocess.Popen(
            ['openssl', 'rand', '-hex', bytes],
            stdout=key_file
        )
    elif base64 is True:
        print(base64, file=sys.stderr)
        p = subprocess.Popen(
            ['openssl', 'rand', '-base64', bytes],
            stdout=key_file
        )

    p.wait()

    key_file = open(key_dir, 'r')

    key = key_file.read()

    data = {
        'key' : key
    }

    return data

def generate_aes_key_iv( bytes ):
    key_dir=os.path.join(UPLOAD_FOLDER, "key-file.txt")
    iv_dir=os.path.join(UPLOAD_FOLDER, "iv-file.txt")
    #print(iv_dir, key_dir)

    key_file = open(key_dir, 'w+')
    iv_file = open(iv_dir, 'w+')
    #print(iv_file, key_file)

    p1 = subprocess.Popen(
        ['openssl', 'rand', '-hex', str(int(bytes))],
        stdout=key_file
    )
    p2 = subprocess.Popen(
        ['openssl', 'rand', '-hex', str(16)],
        stdout=iv_file
    )
    
    exit_codes = [p.wait() for p in [p1, p2]]

    key_file = open(key_dir, 'r')
    iv_file = open(iv_dir, 'r')
    #print(iv_file, key_file)

    iv = iv_file.read()
    key = key_file.read()
    print('IV ' + iv + 'Key ' + key)

    data = {
        'iv' : iv,
        'key' : key
    }

    return data

def generate_3des_key_iv():
    key_dir=os.path.join(UPLOAD_FOLDER, "key-file.txt")
    iv_dir=os.path.join(UPLOAD_FOLDER, "iv-file.txt")
    #print(iv_dir, key_dir)

    key_file = open(key_dir, 'w+')
    iv_file = open(iv_dir, 'w+')
    #print(iv_file, key_file)

    p1 = subprocess.Popen(
        ['openssl', 'rand', '-hex', str(24)],
        stdout=key_file
    )
    p2 = subprocess.Popen(
        ['openssl', 'rand', '-hex', str(8)],
        stdout=iv_file
    )
    
    exit_codes = [p.wait() for p in [p1, p2]]

    key_file = open(key_dir, 'r')
    iv_file = open(iv_dir, 'r')
    #print(iv_file, key_file)

    iv = iv_file.read()
    key = key_file.read()
    print('IV ' + iv + 'Key ' + key)

    data = {
        'iv' : iv,
        'key' : key
    }

    return data

def digest_file( input_file, hash_algorithm ):

    key_dir=os.path.join(UPLOAD_FOLDER, "key-file.txt")
    key_file = open(key_dir, 'w+')

    file_path = os.path.join(UPLOAD_FOLDER, input_file)
    hash = '-' + hash_algorithm

    p1 = subprocess.Popen(
        ['openssl', 'dgst', hash, file_path,],
        stdout=key_file
    )
    p1.wait()
    key_file = open(key_dir, 'r')

    key = key_file.read().split('=')[1]

    print('Key ' + key)

    data = {
        'hash' : key
    }

    return data


def encrypt_file( input_file, key, iv, cipher = None, base64=None):
    file_path = os.path.join(UPLOAD_FOLDER, input_file)
    enc_file = os.path.join(UPLOAD_FOLDER,  input_file + ".enc")

    if cipher is not None:
        print('Cipher selected: ' + cipher, file=sys.stderr)
        input_cipher = '-' + cipher
        print('Encrypting file: ' + str(file_path) +'\nWith Key:  ' +str(key) + 'And IV:   ' +str(iv), file=sys.stderr)
        try:
            if base64 is not None:
                p = subprocess.Popen(
                    ['openssl', 'enc', input_cipher, '-e', '-a', '-in', file_path, '-out', enc_file, '-K', key, '-iv', iv],
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
            else:
                p = subprocess.Popen(
                    ['openssl', 'enc', input_cipher, '-e', '-in', file_path, '-out', enc_file, '-K', key, '-iv', iv],
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
            p.wait()
            return {'ok':'ok'}
        except:
            print('Failed to encrypt: ' + str(file_path), file=sys.stderr)
            return {'error':'failed'}


def decrypt_file( input_file, key, iv, cipher = None, base64=None ):
    file_path = os.path.join(UPLOAD_FOLDER, input_file)
    dec_file = os.path.join(UPLOAD_FOLDER, file_path.rsplit('.',1)[0] + ".dec")

    if cipher is not None:
        print('Cipher selected: ' + cipher, file=sys.stderr)
        input_cipher = '-' + cipher
        print('Decrypting file: ' + str(file_path) +'\nWith Key:  ' +str(key) + 'And IV:   ' +str(iv), file=sys.stderr)
        try:
            if base64 is not None:
                p = subprocess.Popen(
                    ['openssl', 'enc', input_cipher, '-d', '-a', '-in', file_path, '-out', dec_file, '-K', key, '-iv', iv],
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
            else:
                p = subprocess.Popen(
                    ['openssl', 'enc', input_cipher, '-d', '-in', file_path, '-out', dec_file, '-K', key, '-iv', iv],
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
                
            p.wait()
            return {'ok':'ok'}
        except:
            print('Failed to encrypt: ' + str(file_path), file=sys.stderr)
            return {'error':'failed'}