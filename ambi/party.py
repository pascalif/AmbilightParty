__author__ = 'pascal'

from ambi.tv import AmbilightTV
from ambi.txex import BufferedAmbilightTV, Direction

import argparse
import sys
import time
import random


class AmbilightParty():

    def __init__(self, ip):
        self.tv = BufferedAmbilightTV(ip=ip, dryrun=False)
        self.tv.autoconfigure()

    def rotate_auto(self, moves=None, duration=None, speed=1.0, direction=Direction.CCW):
        """ Rotate pixel several time, by duration or by moves number.

        :param moves: Number of rotation shift to doself.set_pixels_by_side(
            left_pixels=self.pixels[AmbiTV.LEFT],
            top_pixels=self.pixels[AmbiTV.TOP],
            right_pixels=self.pixels[AmbiTV.RIGHT],
            bottom_pixels=self.pixels[AmbiTV.BOTTOM])
        :param duration: Or the total duration of animation (in seconds)
        :param speed: Pause between each shift (in seconds)
        :param direction: Rotation direction
        :return: None
        """
        if duration is not None and moves is not None:
            raise Exception('moves and duration are mutually exclusive')

        if moves is not None:
            for i in range(0, moves):
                self.tv.rotate(direction=direction)
                time.sleep(speed)
            return

        if duration is None:
            duration = sys.maxint
        started = time.time()
        while time.time() < started + duration:
            try:
                self.tv.rotate(direction=direction)
                time.sleep(speed)
            except KeyboardInterrupt:
                return

    def get_themes(self):
        return {
            'xmas': [(255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (255, 255, 255), (255, 255, 255)],
            'italia': [(255, 0, 0), (255, 0, 0), (255, 255, 255), (255, 255, 255), (0, 255, 0), (0, 255, 0)],
            'france': [(0, 0, 255), (0, 0, 255), (255, 255, 255), (255, 255, 255), (255, 0, 0), (255, 0, 0)],
            'switzerland': [(255, 0, 0), (255, 0, 0), (255, 255, 255), (255, 255, 255)],
            'usa': [(0, 0, 255), (0, 0, 255), (255, 0, 0), (255, 0, 0), (255, 255, 255), (255, 255, 255)],
            'police': [(0, 0, 255), (0, 0, 0), (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 0)],
            'stpatrick': [(0, 255, 0), (0, 255, 0), (255, 255, 255), (255, 255, 255)],
            'ireland': [(0, 255, 0), (0, 255, 0), (255, 255, 255), (255, 255, 255), (255, 102, 0), (255, 102, 0)],
            'trafficlight': [(255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 96, 0), (255, 96, 0), (0, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 0)],
            'colors1': [(255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 255), (0, 0, 255)],
            'rgb': [(255, 0, 0), (0, 0, 0), (0, 255, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0)],
            'rainbow': [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (143, 0, 255)],
            'rainbow2': [(255, 0, 0), (0, 0, 0), (255, 127, 0), (255, 255, 0), (0, 0, 0), (0, 255, 0), (0, 0, 0), (0, 0, 255), (0, 0, 0), (75, 0, 130), (0, 0, 0), (143, 0, 255), (0, 0, 0)],
            'halloween': [(249, 80, 1), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
            'pastel': [(255, 0, 0), (128, 0, 128), (0, 255, 255), (128, 0, 0), (0, 255, 0), (0, 128, 128),
                        (255, 255, 0), (0, 0, 128), (0, 0, 255), (128, 128, 0), (0, 255, 255), (0, 128, 0)]
        }

    def show_list(self):
        print('Available themes :')
        for theme_name in sorted(self.get_themes().keys()):
            print(' - %s' % theme_name)

    def play_theme(self, pattern_pixels=None, theme_name=None, duration=0, speed=0.1, direction=Direction.CCW):
        if theme_name is not None:
            theme_pixels = self.get_themes()
            if theme_name not in theme_pixels:
                raise Exception('Invalid theme name [{:s}]'.format(theme_name))
            pattern_pixels = theme_pixels[theme_name]

        self.tv.patternize(pattern_pixels)
        self.rotate_auto(duration=duration, speed=speed, direction=direction)

    def demo_all(self):
        print('Reseting pixels')
        self.tv.set_color(255, 255, 64)
        #tv.set_side(AmbiTV.LEFT, 255, 0, 0)
        #tv.set_side(AmbiTV.RIGHT, 0, 255, 0)
        #tv.push_clockwise( 255, 0, 0)
        self.tv.set_pixel(AmbilightTV.TOP, 0, 0, 0, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 1, 0, 0, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 2, 255, 255, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 3, 255, 255, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 4, 255, 0, 0)
        self.tv.set_pixel(AmbilightTV.TOP, 5, 255, 0, 0)
        time.sleep(1)
        self.tv.mirror(Direction.VERTICAL)
        time.sleep(2)
        self.rotate_auto(direction=Direction.CW, moves=1, pause=0.8)
        self.rotate_auto(direction=Direction.CCW, moves=1, pause=0.8)

        # todo test set_pixel with composante en moins

    def demo_themes(self):
        themes = self.get_themes()
        remaining_names = themes.keys()

        for i in range(0, 10):
            direction = random.sample({Direction.CW, Direction.CCW}, 1)[0]
            speed = random.sample({0.1, 0.5, 0.9}, 1)[0]
            theme_name = random.sample(remaining_names, 1)[0]
            remaining_names.remove(theme_name)
            print('Playing theme [%s]' % theme_name)
            self.play_theme(theme_name=theme_name, direction=direction, duration=8, speed=speed)


def main():
    desc = 'Have fun with your Ambilight TV.'

    parser = argparse.ArgumentParser(description=desc, add_help=True)
    parser.add_argument('--info', action='store_true', required=False, default=None,
                        help='Display TV and library info')
    parser.add_argument('--list', action='store_true', required=False, default=None,
                        help='List available themes')

    parser.add_argument('--ip', action='store', required=False, default='192.168.0.59',
                        help='TV ip address')
    parser.add_argument('--stop', action='store_true', required=False, default=None,
                        help='Restore the TV in automatic Ambilight management mode')

    parser.add_argument('--demo', action='store', required=False, default=None,
                        help='Play demo mode')

    parser.add_argument('--color', action='store', required=False, default=None,
                        help='Set a single color on all pixels. Format : RRGGBB, eg FF8800')
    parser.add_argument('--theme', action='store', required=False,
                        help='Name of theme to play')
    parser.add_argument('--duration', action='store', required=False, default=None,
                        help='Duration of animation. None for forever')
    parser.add_argument('--speed', action='store', required=False, default=1000,
                        help='Animation speed in milliseconds')

    args = parser.parse_args()
    party = AmbilightParty(args.ip)

    if args.list:
        party.show_list()

    elif args.info:
        print party.tv.info()
    elif args.stop:
        party.tv.set_mode_internal()
    elif args.color:
        party.tv.set_color(int(args.color[0:2], 16), int(args.color[2:4], 16), int(args.color[4:6], 16))

    elif args.demo is not None:
        if args.demo == 'themes':
            party.demo_themes()
        else:
            party.demo_all()
    elif args.theme:
        party.play_theme(theme_name=args.theme, duration=args.duration, speed=float(args.speed)/1000)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print "Error:", e
        sys.exit(1)
