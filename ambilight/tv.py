import sys
import json
import requests
import os
import copy
from abc import ABCMeta, abstractmethod


class AmilightTVObserver:
    """
    An object being notified of changes in the Ambilight pixels.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """The observer object"""
        self.subject = None

    def register_subject(self, subject):
        self.subject = subject

    def remove_subject(self):
        self.subject = None

    @abstractmethod
    def on_all_pixels_changed(self, red, green, blue):
        """All pixels have been changed"""
        pass

    @abstractmethod
    def on_side_changed(self, side, red, green, blue, layer):
        pass

    @abstractmethod
    def on_single_pixel_changed(self, side, position, red, green, blue, layer):
        pass

    @abstractmethod
    def on_pixels_by_side_changed(self, left_pixels, top_pixels, right_pixels, bottom_pixels, layer):
        pass


class AmbilightTV(object):
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
        self.sizes = {AmbilightTV.LEFT: 0, AmbilightTV.TOP: 0, AmbilightTV.RIGHT: 0, AmbilightTV.BOTTOM: 0}
        self._observer_list = []

    def set_dryrun(self, dryrun):
        self.dryrun = dryrun

    def set_ip(self, ip):
        self.ip = ip

    def register_observer(self, observer):
        if observer not in self._observer_list:
            self._observer_list.append(observer)
            observer.register_subject(self)
        else:
            raise Exception('Observer already registered')

    def unregister_observer(self, observer):
        if observer in self._observer_list:
            observer.remove_subject()
            self._observer_list.remove(observer)
        else:
            raise Exception('Observer not registered')

    def _get_base_url(self):
        url = 'http://' + self.ip + ':' + str(self.port) + '/' + str(self.version) + '/ambilight'
        return url

    def _debug_request(self, r):
        print('')
        print("***** Request   :")
        print('--- encoding    : ' + r.encoding)
        print("--- url         : " + r.url)
        print("--- headers     : ")
        print(r.request.headers)
        print("--- body        : ??? ")
        print("***** Response  :")
        print("--- status code : " + str(r.status_code))
        print("--- headers     : ")
        print(r.headers)
        print("--- text        : " + r.content)
        print("--- json        : ")
        try:
            print(r.json())
        except Exception:
            pass
        print('')

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
        url = self._build_url(endpath)

        if self.dryrun:
            return None

        r = requests.post(url, params=qs, headers=self._build_headers(), data=json.dumps(body))
        #self._debug_request(r)
        return r

    def info(self):
        return {'topology': self.get_topology(), 'lib-version': self.VERSION}

    def has_top(self):
        return self.sizes[AmbilightTV.TOP] != 0

    def has_bottom(self):
        return self.sizes[AmbilightTV.BOTTOM] != 0

    def autoconfigure(self, ip=None):
        if ip is not None:
            self.ip = ip

        js = self.get_topology()
        self.nb_layers = js['layers']
        self.sizes[AmbilightTV.LEFT] = js['left']
        self.sizes[AmbilightTV.TOP] = js['top']
        self.sizes[AmbilightTV.RIGHT] = js['right']
        self.sizes[AmbilightTV.BOTTOM] = js['bottom']
        self.nb_pixels = self.sizes[AmbilightTV.LEFT] + self.sizes[AmbilightTV.TOP] + self.sizes[AmbilightTV.RIGHT] + \
            self.sizes[AmbilightTV.BOTTOM]

    def get_mode(self):
        self.ws_get('/mode')

    def set_mode_internal(self):
        self.ws_post('/mode', body={'current': 'internal'})

    def set_mode_manual(self):
        self.ws_post('/mode', body={'current': 'manual'})

    def get_topology(self):
        if self.dryrun:
            return {"bottom": 0, "layers": 1, "left": 4, "right": 4, "top": 9}

        return self.ws_get('/topology').json()

    def check_parameters(self, side=None, layer=None, position=None):
        if side is not None and side not in [AmbilightTV.LEFT, AmbilightTV.TOP, AmbilightTV.RIGHT, AmbilightTV.BOTTOM]:
            raise Exception('Bad side value ['+str(side)+']')
        if layer is not None and (layer < 0 or layer > self.nb_layers):
            raise Exception('Bad layer value ['+str(layer)+']')
        if position is not None:
            if side is None:
                raise Exception('side parameter must be specified when position is used')
            if self.sizes[side] < position or position < 0:
                raise Exception('Bad position value [%s] for side [%s]' % (position, side))

    def set_color(self, red=None, green=None, blue=None):
        body = {}
        # todo funct to mutualize next lines
        if red is not None:
            body['r'] = red
        if green is not None:
            body['g'] = green
        if blue is not None:
            body['b'] = blue

        self.ws_post('/cached', body=body)

        for observer in self._observer_list:
            observer.on_all_pixels_changed(red=red, green=green, blue=blue)

    def set_black(self):
        self.set_color(red=0, green=0, blue=0)

    def set_white(self):
        self.set_color(red=255, green=255, blue=255)

    def set_red(self):
        self.set_color(red=255, green=0, blue=0)

    def set_green(self):
        self.set_color(red=0, green=255, blue=0)

    def set_blue(self):
        self.set_color(red=0, green=0, blue=255)

    def set_side(self, side, red=None, green=None, blue=None, color=None, layer=1):
        self.check_parameters(side=side, layer=layer)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = self._generate_api_pixel(red, green, blue, color)

        self.ws_post('/cached', body=body)

        for observer in self._observer_list:
            observer.on_side_changed(side=side, red=red, green=green, blue=blue, layer=layer)

    def set_sides(self, left_color=None, top_color=None, right_color=None, bottom_color=None, layer=1):
        self.check_parameters(layer=layer)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        if left_color:
            body[layer_key][AmbilightTV.LEFT] = self._generate_api_pixel(color=left_color)
        if right_color:
            body[layer_key][AmbilightTV.RIGHT] = self._generate_api_pixel(color=right_color)
        if top_color:
            body[layer_key][AmbilightTV.TOP] = self._generate_api_pixel(color=top_color)
        if bottom_color:
            body[layer_key][AmbilightTV.BOTTOM] = self._generate_api_pixel(color=bottom_color)

        self.ws_post('/cached', body=body)

        for observer in self._observer_list:
            if left_color:
                observer.on_side_changed(side=AmbilightTV.LEFT, red=left_color[0], green=left_color[1],
                                         blue=left_color[2], layer=layer)
            if right_color:
                observer.on_side_changed(side=AmbilightTV.RIGHT, red=right_color[0], green=right_color[1],
                                         blue=right_color[2], layer=layer)
            if top_color:
                observer.on_side_changed(side=AmbilightTV.TOP, red=top_color[0], green=top_color[1],
                                         blue=top_color[2], layer=layer)
            if bottom_color:
                observer.on_side_changed(side=AmbilightTV.BOTTOM, red=bottom_color[0], green=bottom_color[1],
                                         blue=bottom_color[2], layer=layer)

    def set_pixel(self, side, position, red=None, green=None, blue=None, color=None, layer=1):
        self.check_parameters(side=side, layer=layer, position=position)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = {}
        body[layer_key][side][position] = self._generate_api_pixel(red, green, blue, color)

        self.ws_post('/cached', body=body)

        for observer in self._observer_list:
            observer.on_single_pixel_changed(side=side, position=position,
                                             red=red, green=green, blue=blue, layer=layer)

    def set_pixels_by_side(self, left_pixels=None, top_pixels=None, right_pixels=None, bottom_pixels=None, layer=1):
        left_pixels = copy.deepcopy(left_pixels)
        top_pixels = copy.deepcopy(top_pixels)
        right_pixels = copy.deepcopy(right_pixels)
        bottom_pixels = copy.deepcopy(bottom_pixels)

        json_layer = {}
        self._inject_pixels_for_side(json_layer, AmbilightTV.LEFT, left_pixels)
        self._inject_pixels_for_side(json_layer, AmbilightTV.TOP, top_pixels)
        self._inject_pixels_for_side(json_layer, AmbilightTV.RIGHT, right_pixels)
        self._inject_pixels_for_side(json_layer, AmbilightTV.BOTTOM, bottom_pixels)
        body = {'layer'+str(layer): json_layer}

        self.ws_post('/cached', body=body)

        for observer in self._observer_list:
            observer.on_pixels_by_side_changed(left_pixels=left_pixels, top_pixels=top_pixels,
                                               right_pixels=right_pixels, bottom_pixels=bottom_pixels, layer=layer)

    @staticmethod
    def _generate_api_pixel(red=None, green=None, blue=None, color=None):
        if color is not None:
            return {'r': color[0], 'g': color[1], 'b': color[2]}

        pixel = {}
        if red is not None:
            pixel['r'] = red
        if green is not None:
            pixel['g'] = green
        if blue is not None:
            pixel['b'] = blue
        return pixel

    @staticmethod
    def _inject_pixels_for_side(dict_for_layer, side, pixels):
        if pixels is None:
            return

        dict_for_layer[side] = {}
        if type(pixels) is list:
            for i in range(0, len(pixels)):
                dict_for_layer[side][str(i)] = {'r': pixels[i][0], 'g': pixels[i][1], 'b': pixels[i][2]}
        elif type(pixels) is dict:
            for pos, pixel in pixels:
                dict_for_layer[side][pos] = {'r': pixel[0], 'g': pixel[1], 'b': pixel[2]}
        else:
            raise Exception('Unexpected type for pixels container')
