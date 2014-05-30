__author__ = 'pascal'

from ambi.tv import AmbiTV
from ambi.txex import AmbiTVExtended, Direction

import argparse
import sys
from time import sleep

# halloween, xmas, stpatrick, 4july/bastille, police car, traffic light, rgb
# rainbow
# sunset


def main():
    desc = 'Have fun with your Ambilight TV.'

    parser = argparse.ArgumentParser(description=desc, add_help=True)
    parser.add_argument('-s', '--speed', action='store', required=False, default=1, help='Animation speed')
    parser.add_argument('--demo', action='store', required=False, default=True, help='Play demo mode')
    args = parser.parse_args()

    tv = AmbiTVExtended(ip='192.168.0.59', dryrun=False)
    tv.autoconfigure()

    if args.demo:
        tv.reset(255,255,64)
        #tv.set_side(AmbiTV.LEFT, 255, 0, 0)
        #tv.set_side(AmbiTV.RIGHT, 0, 255, 0)
        #tv.push_clockwise( 255, 0, 0)

        tv.set_pixel(AmbiTV.TOP, 0 ,0,0,255)
        tv.set_pixel(AmbiTV.TOP, 1 ,0,0,255)
        tv.set_pixel(AmbiTV.TOP, 2 ,255,255,255)
        tv.set_pixel(AmbiTV.TOP, 3 ,255,255,255)
        tv.set_pixel(AmbiTV.TOP, 4 ,255,0,0)
        tv.set_pixel(AmbiTV.TOP, 5 ,255,0,0)
        sleep(1)
        tv.mirror_leftright()
        return

        sleep(1)
        for i in range(0, 20):
            #tv.push_clockwise( 0, 0, 255)
            tv.rotate(direction=Direction.CW)
            sleep(0.05)
        sleep(2)
        tv.mirror_leftright()
    else:
        sleep(1)
        tv.mirror_leftright()
        sleep(1)
        tv.mirror_leftright()
        sleep(1)
        tv.mirror_leftright()
        sleep(1)
        # todo set_pixel with compo en moins

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print "Error:", e
        sys.exit(1)
