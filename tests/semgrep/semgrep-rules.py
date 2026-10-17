import hashlib
import os
import pickle
import ssl
import subprocess
import sqlite3
import tempfile

import httpx
import requests
import yaml


def sql(conn: sqlite3.Connection, user: str):
    # ruleid: reposcan.python.sql-string-concat
    conn.execute("SELECT * FROM t WHERE n = '" + user + "'")
    # ok: reposcan.python.sql-string-concat
    conn.execute("SELECT * FROM t WHERE n = ?", (user,))


def shell(host: str):
    # ruleid: reposcan.python.subprocess-shell-true
    subprocess.call("ping " + host, shell=True)
    # ok: reposcan.python.subprocess-shell-true
    subprocess.call(["ping", host])


def evaluate(x: str):
    # ruleid: reposcan.python.eval-call
    eval(x)
    # ok: reposcan.python.eval-call
    eval("1 + 1")


def digest(b: bytes):
    # ruleid: reposcan.python.weak-hash
    hashlib.md5(b)
    # ruleid: reposcan.python.weak-hash
    hashlib.sha1(b)
    # ok: reposcan.python.weak-hash
    hashlib.sha256(b)


def load_yaml(text: str):
    # ruleid: reposcan.python.yaml-unsafe-load
    yaml.load(text)
    # ruleid: reposcan.python.yaml-unsafe-load
    yaml.load(text, Loader=yaml.Loader)
    # ruleid: reposcan.python.yaml-unsafe-load
    yaml.load(text, Loader=yaml.UnsafeLoader)
    # ok: reposcan.python.yaml-unsafe-load
    yaml.safe_load(text)
    # ok: reposcan.python.yaml-unsafe-load
    yaml.load(text, Loader=yaml.SafeLoader)


def unpickle(data: bytes, fh):
    # ruleid: reposcan.python.pickle-load
    pickle.loads(data)
    # ruleid: reposcan.python.pickle-load
    pickle.load(fh)
    # ok: reposcan.python.pickle-load
    pickle.dumps({"a": 1})


def run_code(code: str):
    # ruleid: reposcan.python.exec-call
    exec(code)
    # ok: reposcan.python.exec-call
    exec("x = 1")


def system(cmd: str):
    # ruleid: reposcan.python.os-system
    os.system(cmd)
    # ok: reposcan.python.os-system
    os.system("clear")


def http(url: str):
    # ruleid: reposcan.python.requests-verify-false
    requests.get(url, verify=False)
    # ruleid: reposcan.python.requests-verify-false
    httpx.post(url, verify=False, timeout=3)
    # ok: reposcan.python.requests-verify-false
    requests.get(url, verify=True)
    # ok: reposcan.python.requests-verify-false
    requests.get(url)


def contexts():
    # ruleid: reposcan.python.ssl-unverified-context
    ssl._create_unverified_context()
    ctx = ssl.create_default_context()
    # ruleid: reposcan.python.ssl-unverified-context
    ctx.verify_mode = ssl.CERT_NONE
    # ok: reposcan.python.ssl-unverified-context
    ctx.verify_mode = ssl.CERT_REQUIRED


def temp():
    # ruleid: reposcan.python.tempfile-mktemp
    tempfile.mktemp()
    # ok: reposcan.python.tempfile-mktemp
    tempfile.mkstemp()


def serve(app):
    # ruleid: reposcan.python.flask-debug-enabled
    app.run(host="0.0.0.0", debug=True)
    # ok: reposcan.python.flask-debug-enabled
    app.run(host="127.0.0.1", debug=False)
