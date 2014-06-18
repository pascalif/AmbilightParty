__author__ = 'pascal'

from tv import AmbiTV
from array import array


class Direction():
    CCW = 1
    CW = 0
    VERTICAL = 1
    HORIZONTAL = 0


class AmbiTVExtended(AmbiTV):

    def __init__(self, ip=None, dryrun=False):
        super(AmbiTVExtended, self).__init__(ip, dryrun)
        self.set_listener(self)
        self.pixels = {AmbiTV.LEFT: [], AmbiTV.TOP: [], AmbiTV.RIGHT: [], AmbiTV.BOTTOM: []}
        self.nb_pixels = 0

    def autoconfigure(self):
        super(AmbiTVExtended, self).autoconfigure()
        for i in range(0, self.sizes[AmbiTV.LEFT]):
            self.pixels[AmbiTV.LEFT].append((0, 0, 0))
        for i in range(0, self.sizes[AmbiTV.TOP]):
            self.pixels[AmbiTV.TOP].append((0, 0, 0))
        for i in range(0, self.sizes[AmbiTV.RIGHT]):
            self.pixels[AmbiTV.RIGHT].append((0, 0, 0))
        for i in range(0, self.sizes[AmbiTV.BOTTOM]):
            self.pixels[AmbiTV.BOTTOM].append((0, 0, 0))

    def notified_reset(self, red, green, blue):
        #print "notify_resetted :"+str(red)+str(green)+str(blue)
        for side in self.pixels.keys():
            for i in range(0, self.sizes[side]):
                self.pixels[side][i] = (red, green, blue)

    def on_side_changed(self, side, red, green, blue, layer):
        #print "on_side_changed :"+side + " : "+str(red)+str(green)+str(blue)
        for i in range(0, self.sizes[side]):
            self.pixels[side][i] = (red, green, blue)

    def on_single_pixel_changed(self, side, position, red, green, blue, layer):
        #print "on_single_pixel_changed :"+side + " : "+str(position) + " : " +str(red)+str(green)+str(blue)
        self.pixels[side][position] = (red, green, blue)

    def on_pixels_by_side_changed(self, left_pixels, top_pixels, right_pixels, bottom_pixels, layer):
        #print "on_pixels_by_side_changed "
        self._on_pixels_by_side_changed(side=AmbiTV.LEFT, pixels=left_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbiTV.TOP, pixels=top_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbiTV.RIGHT, pixels=right_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbiTV.BOTTOM, pixels=bottom_pixels, layer=layer)

    def _on_pixels_by_side_changed(self, side, pixels, layer):
        if pixels is None:
            return

        if type(pixels) is list:
            for pos in range(0, len(pixels)):
                self.pixels[side][pos] = pixels[pos]
        else:
            for pixel_pos, pixel in pixels.iteritems():
                self.pixels[side][pixel_pos] = pixel

    def _serialize_pixels(self):
        all_pixels = self.pixels[AmbiTV.LEFT] + self.pixels[AmbiTV.TOP] + self.pixels[AmbiTV.RIGHT] + \
                 self.pixels[AmbiTV.BOTTOM]
        return all_pixels

    def _unserialize_pixels(self, all_pixels):
        self.pixels[AmbiTV.LEFT] = all_pixels[
            0:
            self.sizes[AmbiTV.LEFT]]
        self.pixels[AmbiTV.TOP] = all_pixels[
            self.sizes[AmbiTV.LEFT]:
            self.sizes[AmbiTV.LEFT]+self.sizes[AmbiTV.TOP]]
        self.pixels[AmbiTV.RIGHT] = all_pixels[
            self.sizes[AmbiTV.LEFT]+self.sizes[AmbiTV.TOP]:
            self.sizes[AmbiTV.LEFT]+self.sizes[AmbiTV.TOP]+self.sizes[AmbiTV.RIGHT]]
        self.pixels[AmbiTV.BOTTOM] = all_pixels[
            self.sizes[AmbiTV.LEFT]+self.sizes[AmbiTV.TOP]+self.sizes[AmbiTV.RIGHT]:]

    def _send_pixels(self):
        self.set_pixels_by_side(
            left_pixels=self.pixels[AmbiTV.LEFT],
            top_pixels=self.pixels[AmbiTV.TOP],
            right_pixels=self.pixels[AmbiTV.RIGHT],
            bottom_pixels=self.pixels[AmbiTV.BOTTOM])

    def patternize(self, pattern_pixels):
        all_pixels = self._serialize_pixels()
        nb_pixels_before = len(all_pixels)
        for pos in range(0, len(all_pixels), len(pattern_pixels)):
            all_pixels[pos : pos+len(pattern_pixels)] = pattern_pixels
        # truncate potentially surnumerous pattern pixels added at the end
        del all_pixels[nb_pixels_before:]
        self._unserialize_pixels(all_pixels)
        self._send_pixels()

    # TODO inject_side=AmbiTV.LEFT, inject_position=0
    # TODO loop or drop
    def push_clockwise(self, red=None, green=None, blue=None, color=None):
        new_pixel = self._read_color_as_tuple(red, green, blue, color)
        all_pixels = self._serialize_pixels()

        for pos in range(len(all_pixels)-1, 0, -1):
            all_pixels[pos] = all_pixels[pos-1]
        all_pixels[0] = new_pixel

        self._unserialize_pixels(all_pixels)
        self._send_pixels()

    def rotate(self, direction=Direction.CCW):
        all_pixels = self._serialize_pixels()

        if direction == Direction.CCW:
            initial_last_pixel = all_pixels[len(all_pixels)-1]
            for pos in range(len(all_pixels)-1, 0, -1):
                all_pixels[pos] = all_pixels[pos-1]
            all_pixels[0] = initial_last_pixel
        else:
            initial_first_pixel = all_pixels[0]
            for pos in range(0, len(all_pixels)-1, 1):
                all_pixels[pos] = all_pixels[pos+1]
            all_pixels[len(all_pixels)-1] = initial_first_pixel

        self._unserialize_pixels(all_pixels)
        self._send_pixels()

    def mirror(self, direction):
        # TODO inverse TOP/BOTTOM too
        if direction == Direction.VERTICAL:
            self.set_pixels_by_side(left_pixels=self.pixels[AmbiTV.RIGHT], right_pixels=self.pixels[AmbiTV.LEFT])
                        # i[b], i[a] = i[a], i[b]
        # tester both