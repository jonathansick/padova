#!/usr/bin/env python
# encoding: utf-8
"""
Send a sample request to the CMD interface.

2013-11-29 - Created by Jonathan Sick
"""

from padova.cmd import CMD


def main():
    cmd = CMD()
    cache_path = cmd.get()
    print cache_path


if __name__ == '__main__':
    main()
