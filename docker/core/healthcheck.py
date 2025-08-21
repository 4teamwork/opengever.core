#!/usr/local/bin/python
import socket
import sys


def netcat(hostname, port, content, timeout=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout is not None:
        s.settimeout(timeout)
    s.connect((hostname, port))
    s.sendall(content)
    reply = ''
    while 1:
        data = s.recv(1024)
        if data == '':
            break
        reply += data
    s.close()
    return reply


try:
    res = netcat('127.0.0.1', 8160, 'health_check\n')
except socket.error as exc:
    res = str(exc)

if res.strip() == 'OK':
    exit_code = 0
else:
    exit_code = 1
print(res)
sys.exit(exit_code)
