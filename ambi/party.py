from ambi.tv import AmbiTV

__author__ = 'pascal'

import argparse
import sys
from time import sleep


def main():
    desc = 'Have fun with your Ambilight TV.'

    parser = argparse.ArgumentParser(description=desc, add_help=True)
    parser.add_argument('-s', '--speed', action='store', required=False, default=1, help='Animation speed')
    args = parser.parse_args()

    tv = AmbiTV('192.168.0.59')
    tv.autoconfigure()
    tv.set_side(AmbiTV.TOP, 255, 0, 0)
    tv.set_pixel(AmbiTV.TOP, 2, 0, 255, 0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print "Error:", e
        sys.exit(1)
