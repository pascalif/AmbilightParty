import sys
import json
from tarfile import _ringbuffer
import requests
import os
import copy

class AmbiTV(object):
    LEFT = 'left'
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'
    VERSION = 1.0

    def __init__(self, ip=None, dryrun=False):
        self.dryrun = dryrun
        self.ip = ip
        self.port = 1925
        self.version = 1
        self.nb_layers = 0
        self.nb_pixels = 0
        self.sizes = {AmbiTV.LEFT: 0, AmbiTV.TOP: 0, AmbiTV.RIGHT: 0, AmbiTV.BOTTOM: 0}
        self.listener = None

    def set_dryrun(self, dryrun):
        self.dryrun = dryrun

    def set_ip(self, ip):
        self.ip = ip

    def set_listener(self, listener):
        self.listener = listener

    def _get_base_url(self):
        url = 'http://' + self.ip + ':' + str(self.port) + '/' + str(self.version) + '/ambilight'
        return url

    def _debug_request(self, r):
        print ''
        print "***** Request   :"
        print '--- encoding    : ' + r.encoding
        print "--- url         : " + r.url
        print "--- headers     : "
        print r.request.headers
        print "--- body        : ??? "
        print "***** Response  :"
        print "--- status code : " + str(r.status_code)
        print "--- headers     : "
        print r.headers
        print "--- text        : " + r.content
        print "--- json        : "
        try:
            print r.json()
        except Exception, e:
            pass
        print ''

    def _build_url(self, endpath):
        url = self._get_base_url()+endpath
        return url

    def _build_headers(self):
        headers = {'User-Agent': 'AmbilightParty-1.00',
                   'Content-Type': 'application/json; charset=UTF-8'}
        return headers

    def ws_get(self, endpath, qs=None):
        url = self._build_url(endpath)

        if self.dryrun:
            return None

        r = requests.get(url, params=qs, headers=self._build_headers())
        #self._debug_request(r)
        return r

    def ws_post(self, endpath, qs=None, body=None):
        #print body
        url = self._build_url(endpath)

        if self.dryrun:
            return None

        r = requests.post(url, params=qs, headers=self._build_headers(), data=json.dumps(body))
        #self._debug_request(r)
        return r

    def info(self):
        return { 'topology': self.get_topology(), 'lib-version': self.VERSION}

    def autoconfigure(self):
        js = self.get_topology()
        self.nb_layers = js['layers']
        self.sizes[AmbiTV.LEFT] = js['left']
        self.sizes[AmbiTV.TOP] = js['top']
        self.sizes[AmbiTV.RIGHT] = js['right']
        self.sizes[AmbiTV.BOTTOM] = js['bottom']
        self.nb_pixels = self.sizes[AmbiTV.LEFT] + self.sizes[AmbiTV.TOP] + self.sizes[AmbiTV.RIGHT] + \
            self.sizes[AmbiTV.BOTTOM]

        self.set_mode_manual()

    def get_mode(self):
        # todo dryrun
        self.ws_get('/mode')

    def set_mode_internal(self):
        # todo dryrun
        self.ws_post('/mode', body={'current': 'internal'})

    def set_mode_manual(self):
        # todo dryrun
        self.ws_post('/mode', body={'current': 'manual'})

    def get_topology(self):
        if self.dryrun:
            return {"bottom": 0, "layers": 1, "left": 4, "right": 4, "top": 9}

        return self.ws_get('/topology').json()

    def check_parameters(self, side=None, layer=None, position=None):
        if side is not None and side not in [AmbiTV.LEFT, AmbiTV.TOP, AmbiTV.RIGHT, AmbiTV.BOTTOM]:
            raise Exception('Bad side value ['+str(side)+']')
        if layer is not None and (layer < 0 or layer > self.nb_layers):
            raise Exception('Bad layer value ['+str(layer)+']')
        if position is not None and (position < 0):
            #TODO check by side
            raise Exception('Bad layer value ['+str(position)+']')

    def reset(self, red=None, green=None, blue=None):
        body = {}
        # todo funct to mutualize next lines
        if red is not None:
            body['r'] = red
        if green is not None:
            body['g'] = green
        if blue is not None:
            body['b'] = blue

        self.ws_post('/cached', body=body)

        if self.listener is not None:
            self.listener.notified_reset(red=red, green=green, blue=blue)

    def reset_black(self):
        self.reset(red=0, green=0, blue=0)

    def reset_white(self):
        self.reset(red=255, green=255, blue=255)

    def reset_red(self):
        self.reset(red=255, green=0, blue=0)

    def reset_blue(self):
        self.reset(red=0, green=0, blue=255)

    def _read_color(self, red=None, green=None, blue=None, color=None):
        if color is not None:
            return {'r': color[0], 'g': color[1], 'b': color[2]}

        struct = {}
        if red is not None:
            struct['r'] = red
        if green is not None:
            struct['g'] = green
        if blue is not None:
            struct['b'] = blue
        return struct

    def _read_color_as_tuple(self, red=None, green=None, blue=None, color=None):
        if color is not None:
            return color[0], color[1], color[2]
        else:
            return red, green, blue

    def set_side(self, side, red=None, green=None, blue=None, color=None, layer=1):
        self.check_parameters(side=side, layer=layer)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = self._read_color(red=red, green=green, blue=blue, color=color)

        self.ws_post('/cached', body=body)

        if self.listener is not None:
            self.listener.on_side_changed(side=side, red=red, green=green, blue=blue, layer=layer)

    def set_pixel(self, side, position, red=None, green=None, blue=None, color=None, layer=1):
        self.check_parameters(side=side, layer=layer, position=position)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = {}
        body[layer_key][side][position] = {}

        if color is not None:
            body[layer_key][side][position] = {'r': color[0], 'g': color[1], 'b': color[2]}
        else:
            if red is not None:
                body[layer_key][side][position]['r'] = red
            if green is not None:
                body[layer_key][side][position]['g'] = green
            if blue is not None:
                body[layer_key][side][position]['b'] = blue

        self.ws_post('/cached', body=body)

        if self.listener is not None:
            self.listener.on_single_pixel_changed(side=side, position=position, red=red, green=green, blue=blue, layer=layer)

    def set_pixels_by_side(self, left_pixels=None, top_pixels=None, right_pixels=None, bottom_pixels=None, layer=1):
        left_pixels = copy.deepcopy(left_pixels)
        top_pixels = copy.deepcopy(top_pixels)
        right_pixels = copy.deepcopy(right_pixels)
        bottom_pixels = copy.deepcopy(bottom_pixels)

        json_layer = {}
        self._inject_pixels_for_side(json_layer, AmbiTV.LEFT, left_pixels)
        self._inject_pixels_for_side(json_layer, AmbiTV.TOP, top_pixels)
        self._inject_pixels_for_side(json_layer, AmbiTV.RIGHT, right_pixels)
        self._inject_pixels_for_side(json_layer, AmbiTV.BOTTOM, bottom_pixels)
        body = {'layer'+str(layer): json_layer}

        self.ws_post('/cached', body=body)

        if self.listener is not None:
            self.listener.on_pixels_by_side_changed(left_pixels=left_pixels, top_pixels=top_pixels,
                                                    right_pixels=right_pixels, bottom_pixels=bottom_pixels, layer=layer)


    def _inject_pixels_for_side(self, json_layer, side, pixels):
        if pixels is None:
            return

        json_layer[side] = {}
        if type(pixels) is list:
            for i in range(0, len(pixels)):
                json_layer[side][str(i)] = {'r': pixels[i][0], 'g': pixels[i][1], 'b': pixels[i][2]}
        elif type(pixels) is dict:
            for pos, pixel in pixels:
                json_layer[side][pos] = {'r': pixel[0], 'g': pixel[1], 'b': pixel[2]}
        else:
            raise Exception('Unexpected type for pixels container')