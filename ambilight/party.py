__author__ = 'pascal'

from ambilight.tv import AmbilightTV
from ambilight.tvbuff import BufferedAmbilightTV, Direction

import argparse
import sys
import time
import random
import json
import os
import ambilight


class AmbilightParty():

    def __init__(self, dryrun=False):
        self.tv = BufferedAmbilightTV(dryrun=dryrun)
        self._caterpillars = None
        self._flags = None

    def connect(self, ip=None):
        self.tv.autoconfigure(ip=ip)

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

    def load_builtin_caterpillars(self):
        builtin_filename = os.path.join(ambilight.__path__[0], 'data', 'caterpillars.json')
        try:
            with open(builtin_filename) as fp:
                js = json.load(fp)
                return js
        except IOError:
            raise Exception('Built-in caterpillars file [%s] not found' % builtin_filename)

    def load_builtin_flags(self):
        builtin_filename = os.path.join(ambilight.__path__[0], 'data', 'flags.json')
        try:
            with open(builtin_filename) as fp:
                js = json.load(fp)
                return js
        except IOError:
            raise Exception('Built-in flags file [%s] not found' % builtin_filename)

    def get_caterpillars(self):
        if self._caterpillars is None:
            self._caterpillars = self.load_builtin_caterpillars()
        return self._caterpillars

    def get_flags(self):
        if self._flags is None:
            self._flags = self.load_builtin_flags()
        return self._flags

    def show_themes_list(self):
        print('Available themes :')
        print('    * Caterpillars :')
        for caterpillar_name in sorted(self.get_caterpillars().keys()):
            print('        - %s' % caterpillar_name)
        print('    * Flags :')
        for flag_name in sorted(self.get_flags().keys()):
            print('        - %s' % flag_name)

    def play_caterpillar(self, pattern_pixels=None, caterpillar_name=None,
                         duration=0,
                         speed=0.1,
                         direction=Direction.CCW):
        if caterpillar_name is not None:
            caterpillars = self.get_caterpillars()
            if caterpillar_name not in caterpillars:
                raise Exception('Invalid caterpillar name [{:s}]'.format(caterpillar_name))
            pattern_pixels = caterpillars[caterpillar_name]

        self.tv.patternize(pattern_pixels)
        self.rotate_auto(duration=duration, speed=speed, direction=direction)

    def play_flag(self, flag_name=None):
        flags = self.get_flags()
        if flag_name not in flags:
            raise Exception('Invalid flag name [{:s}]'.format(flag_name))
        flag_conf = flags[flag_name]
        flag_type = flag_conf['type']
        colors = flag_conf['colors']

        if flag_type == '3V':
            self.tv.set_sides(left_color=colors[0],
                              right_color=colors[2],
                              top_color=colors[1],
                              bottom_color=colors[1])

        elif flag_type == '3H':
            if self.tv.has_bottom():
                self.tv.set_sides(top_color=colors[0],
                                  left_color=colors[1],
                                  right_color=colors[1],
                                  bottom_color=colors[2])
            else:
                self.tv.set_side(AmbilightTV.TOP, color=colors[0])
                side_size = self.tv.sizes[AmbilightTV.LEFT]
                for i in range(0, side_size/2):
                    self.tv.set_pixel(AmbilightTV.LEFT, i, color=colors[2])
                    self.tv.set_pixel(AmbilightTV.RIGHT, i+side_size/2, color=colors[2])
                for i in range(side_size/2, side_size):
                    self.tv.set_pixel(AmbilightTV.LEFT, i, color=colors[1])
                    self.tv.set_pixel(AmbilightTV.RIGHT, i-side_size/2, color=colors[1])

        else:
            raise Exception('Invalid flag type [{:s}]'.format(flag_type))

    def play_flickering_flag(self, flag_name, duration_flag=1, duration_black=0.6, nb_display=10):
        for i in range(0, nb_display):
            self.play_flag(flag_name)
            time.sleep(duration_flag)
            self.tv.set_black()
            time.sleep(duration_black)

    def demo_basic(self):
        print('Color everywhere...')
        self.tv.set_color(255, 255, 255)
        time.sleep(1)
        self.tv.set_color(0, 0, 0)
        time.sleep(1)
        self.tv.set_color(255, 255, 0)
        time.sleep(1)
        self.tv.set_color(64, 128, 255)
        time.sleep(1)
        self.tv.set_color(255, 0, 0)
        time.sleep(1.5)

        print('Color by side...')
        self.tv.set_side(AmbilightTV.LEFT, 0, 80, 255)
        time.sleep(1)
        self.tv.set_side(AmbilightTV.TOP, 224, 80, 0)
        time.sleep(1)
        self.tv.set_side(AmbilightTV.RIGHT, 80, 255, 0)
        time.sleep(1.5)

        print('Color by pixel...')
        self.tv.set_pixel(AmbilightTV.LEFT, 0, 255, 0, 0)
        self.tv.set_pixel(AmbilightTV.LEFT, 1, 255, 0, 0)
        self.tv.set_pixel(AmbilightTV.TOP, 3, 128, 0, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 4, 128, 0, 255)
        self.tv.set_pixel(AmbilightTV.TOP, 5, 128, 0, 255)
        self.tv.set_pixel(AmbilightTV.RIGHT, 2, 255, 0, 0)
        self.tv.set_pixel(AmbilightTV.RIGHT, 3, 255, 0, 0)

        print('Mirrors...')
        for i in range(0, 6):
            self.tv.mirror(Direction.HORIZONTAL)
            time.sleep(0.7)
        if self.tv.has_bottom():
            for i in range(0, 6):
                self.tv.mirror(Direction.VERTICAL)
                time.sleep(0.7)

        print('Rotations...')
        self.rotate_auto(direction=Direction.CW, moves=12, speed=0.3)
        time.sleep(1)
        self.rotate_auto(direction=Direction.CCW, moves=12, speed=0.3)
        time.sleep(1)

        print('Setting sub-pixels...')
        self.tv.set_color(0, 0, 0)
        for i in range(0, 120):
            self.tv.set_color(0, 0, i)
        for i in range(0, 120):
            self.tv.set_color(i, 0, 0)
        for i in range(0, 120):
            self.tv.set_color(green=i)
        for i in range(120, 0, -1):
            self.tv.set_side(AmbilightTV.TOP, green=i)

        print('End of basic demo :)')

    def demo_kitt(self, speed=0.1, nb_pixels=1):
        self.tv.set_color(0, 0, 0)
        for i in range(0, nb_pixels):
            self.tv.set_pixel(AmbilightTV.TOP, i, 255, 0, 0)

        for i in range(0, 20000):
            self.rotate_auto(direction=Direction.CCW, moves=self.tv.sizes[AmbilightTV.TOP]-nb_pixels, speed=speed)
            self.rotate_auto(direction=Direction.CW, moves=self.tv.sizes[AmbilightTV.TOP]-nb_pixels, speed=speed)

    def demo_caterpillars(self):
        themes = self.get_caterpillars()
        remaining_names = themes.keys()

        for i in range(0, 10):
            direction = random.sample({Direction.CW, Direction.CCW}, 1)[0]
            speed = random.sample({0.1, 0.5, 0.9}, 1)[0]
            caterpillar_name = random.sample(remaining_names, 1)[0]
            remaining_names.remove(caterpillar_name)
            print('Playing caterpillar [%s]' % caterpillar_name)
            self.play_caterpillar(caterpillar_name=caterpillar_name, direction=direction, duration=6, speed=speed)

    def demo_flags(self):
        flags = self.get_flags()
        remaining_names = flags.keys()

        for i in range(0, 5):
            flag_name = random.sample(remaining_names, 1)[0]
            remaining_names.remove(flag_name)
            print('Displaying flag [%s]' % flag_name)
            self.play_flag(flag_name=flag_name)
            time.sleep(2)


def main():
    desc = 'Have fun with your Ambilight TV.'

    parser = argparse.ArgumentParser(description=desc, add_help=True)
    parser.add_argument('--info', action='store_true', required=False, default=None,
                        help='Display TV and library info')
    parser.add_argument('--list', action='store_true', required=False, default=None,
                        help='List available caterpillars and flags')

    parser.add_argument('--ip', action='store', required=False, default='192.168.0.59',
                        help='TV ip address')
    parser.add_argument('--stop', action='store_true', required=False, default=None,
                        help='Restore the TV in automatic Ambilight management mode')

    parser.add_argument('--demo', action='store', required=False, default=None,
                        help='Play a demo mode', choices=['basic', 'caterpillars', 'flags', 'kitt'])

    parser.add_argument('--color', action='store', required=False, default=None,
                        help='Set a single color on all pixels. Format : RRGGBB, eg FF8800')
    parser.add_argument('--caterpillar', action='store', required=False,
                        help='Name of the caterpillar to play')
    parser.add_argument('--direction', action='store', required=False, default='ccw',
                        help='Direction of caterpillar', choices=['cw', 'ccw'])
    parser.add_argument('--flag', action='store', required=False,
                        help='Name of the flag to display')
    parser.add_argument('--flag-flicker', action='store', required=False, default=0,
                        help='Number of flag flickering cycles. 0 to disabled the effect.')

    parser.add_argument('--duration', action='store', required=False, default=None,
                        help='Duration of animation. None for forever')
    parser.add_argument('--speed', action='store', required=False, default=1000,
                        help='Animation speed in milliseconds')

    args = parser.parse_args()
    party = AmbilightParty()
    speed_seconds = float(args.speed)/1000

    if args.list:
        party.show_themes_list()
        exit()

    party.connect(args.ip)
    if args.info:
        print(party.tv.info())
        exit()
    elif args.stop:
        party.tv.set_mode_internal()
        exit()

    party.tv.set_mode_manual()
    if args.color:
        party.tv.set_color(int(args.color[0:2], 16), int(args.color[2:4], 16), int(args.color[4:6], 16))

    elif args.demo is not None:
        if args.demo == 'caterpillars':
            party.demo_caterpillars()
        elif args.demo == 'flags':
            party.demo_flags()
        elif args.demo == 'kitt':
            party.demo_kitt(speed=speed_seconds, nb_pixels=1)
        else:
            party.demo_basic()

    elif args.caterpillar:
        direction = Direction.CW if args.direction == 'cw' else Direction.CCW
        party.play_caterpillar(caterpillar_name=args.caterpillar, duration=args.duration, speed=speed_seconds,
                               direction=direction)
    elif args.flag:
        if args.flag_flicker:
            party.play_flickering_flag(flag_name=args.flag, nb_display=int(args.flag_flicker))
        else:
            party.play_flag(flag_name=args.flag)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)
        sys.exit(1)
