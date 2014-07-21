__author__ = 'pascal'

from tv import AmbilightTV

class Direction():
    CCW = 1
    CW = 0
    VERTICAL = 1
    HORIZONTAL = 0


class BufferedAmbilightTV(AmbilightTV):

    def __init__(self, ip=None, dryrun=False):
        super(BufferedAmbilightTV, self).__init__(ip=ip, dryrun=dryrun)
        self.register_observer(self)

        # Each pixel will be a (r, g, b) tuple
        self.pixels = {AmbilightTV.LEFT: [], AmbilightTV.TOP: [], AmbilightTV.RIGHT: [], AmbilightTV.BOTTOM: []}
        self.nb_pixels = 0

    def register_subject(self, subject):
        pass

    def autoconfigure(self, ip=None):
        super(BufferedAmbilightTV, self).autoconfigure(ip=ip)

        for i in range(0, self.sizes[AmbilightTV.LEFT]):
            self.pixels[AmbilightTV.LEFT].append((0, 0, 0))
        for i in range(0, self.sizes[AmbilightTV.TOP]):
            self.pixels[AmbilightTV.TOP].append((0, 0, 0))
        for i in range(0, self.sizes[AmbilightTV.RIGHT]):
            self.pixels[AmbilightTV.RIGHT].append((0, 0, 0))
        for i in range(0, self.sizes[AmbilightTV.BOTTOM]):
            self.pixels[AmbilightTV.BOTTOM].append((0, 0, 0))

    def load_current_pixels(self):
        raise Exception('TODO Not implemented function load_current_pixels')

    def on_all_pixels_changed(self, red, green, blue):
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
        self._on_pixels_by_side_changed(side=AmbilightTV.LEFT, pixels=left_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbilightTV.TOP, pixels=top_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbilightTV.RIGHT, pixels=right_pixels, layer=layer)
        self._on_pixels_by_side_changed(side=AmbilightTV.BOTTOM, pixels=bottom_pixels, layer=layer)

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
        all_pixels = self.pixels[AmbilightTV.LEFT] + self.pixels[AmbilightTV.TOP] + self.pixels[AmbilightTV.RIGHT] + \
                     self.pixels[AmbilightTV.BOTTOM]
        return all_pixels

    def _unserialize_pixels(self, all_pixels):
        self.pixels[AmbilightTV.LEFT] = all_pixels[
            0:
            self.sizes[AmbilightTV.LEFT]]
        self.pixels[AmbilightTV.TOP] = all_pixels[
            self.sizes[AmbilightTV.LEFT]:
            self.sizes[AmbilightTV.LEFT]+self.sizes[AmbilightTV.TOP]]
        self.pixels[AmbilightTV.RIGHT] = all_pixels[
            self.sizes[AmbilightTV.LEFT]+self.sizes[AmbilightTV.TOP]:
            self.sizes[AmbilightTV.LEFT]+self.sizes[AmbilightTV.TOP]+self.sizes[AmbilightTV.RIGHT]]
        self.pixels[AmbilightTV.BOTTOM] = all_pixels[
            self.sizes[AmbilightTV.LEFT]+self.sizes[AmbilightTV.TOP]+self.sizes[AmbilightTV.RIGHT]:]

    def _send_pixels(self):
        self.set_pixels_by_side(
            left_pixels=self.pixels[AmbilightTV.LEFT],
            top_pixels=self.pixels[AmbilightTV.TOP],
            right_pixels=self.pixels[AmbilightTV.RIGHT],
            bottom_pixels=self.pixels[AmbilightTV.BOTTOM])

    def patternize(self, pattern_pixels):
        all_pixels = self._serialize_pixels()
        nb_pixels_before = len(all_pixels)
        for pos in range(0, len(all_pixels), len(pattern_pixels)):
            all_pixels[pos: pos+len(pattern_pixels)] = pattern_pixels
        # truncate potentially surnumerous pattern pixels added at the end
        del all_pixels[nb_pixels_before:]
        self._unserialize_pixels(all_pixels)
        self._send_pixels()

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
        if direction == Direction.HORIZONTAL:
            self.set_pixels_by_side(left_pixels=self.pixels[AmbilightTV.RIGHT],
                                    right_pixels=self.pixels[AmbilightTV.LEFT])
        else:
            self.set_pixels_by_side(top_pixels=self.pixels[AmbilightTV.BOTTOM],
                                    bottom_pixels=self.pixels[AmbilightTV.TOP])
