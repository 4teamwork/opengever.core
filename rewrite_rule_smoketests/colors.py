def green(msg):
    return '\x1b[32m%s\x1b(B\x1b[m' % msg


def yellow(msg):
    return '\x1b[93m%s\x1b(B\x1b[m' % msg


def red(msg):
    return '\x1b[31m%s\x1b(B\x1b[m' % msg


def white(msg):
    return '\x1b[97m%s\x1b(B\x1b[m' % msg
