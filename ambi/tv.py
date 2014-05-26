import sys
import json
import requests
import os


class AmbiTV():
    LEFT = 'left'
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'

    def __init__(self, ip=None):
        self.ip = ip
        self.port = 1925
        self.version = 1
        self.nb_layers = 1
        self.size_left = 0
        self.size_top = 0
        self.size_right = 0
        self.size_bottom = 0

    def set_ip(self, ip):
        self.ip = ip

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

        r = requests.get(url, params=qs, headers=self._build_headers())
        self._debug_request(r)
        return r

    def ws_post(self, endpath, qs=None, body=None):
        print body
        url = self._build_url(endpath)

        r = requests.post(url, params=qs, headers=self._build_headers(), data=json.dumps(body))
        self._debug_request(r)
        return r

    def autoconfigure(self):
        js = self.get_topology()
        self.nb_layers = js['layers']
        self.size_left = js['left']
        self.size_top = js['top']
        self.size_right = js['right']
        self.size_bottom = js['bottom']

        self.get_mode()
        self.set_mode_manual()
        self.get_mode()

    def get_mode(self):
        self.ws_get('/mode')

    def set_mode_internal(self):
        self.ws_post('/mode', body={'current': 'internal'})

    def set_mode_manual(self):
        self.ws_post('/mode', body={'current': 'manual'})

    def get_topology(self):
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
        if red is not None:
            body['r'] = red
        if green is not None:
            body['g'] = green
        if blue is not None:
            body['b'] = blue

        self.ws_post('/cached', body=body)

    def reset_black(self):
        self.reset(red=0, green=0, blue=0)

    def reset_white(self):
        self.reset(red=255, green=255, blue=255)

    def reset_red(self):
        self.reset(red=255, green=0, blue=0)

    def reset_blue(self):
        self.reset(red=0, green=0, blue=255)

    def set_side(self, side, red=None, green=None, blue=None, layer=1):
        self.check_parameters(side=side, layer=layer)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = {}
        if red is not None:
            body[layer_key][side]['r'] = red
        if green is not None:
            body[layer_key][side]['g'] = green
        if blue is not None:
            body[layer_key][side]['b'] = blue

        self.ws_post('/cached', body=body)

    def set_pixel(self, side, position, red=None, green=None, blue=None, layer=1):
        self.check_parameters(side=side, layer=layer, position=position)
        layer_key = 'layer'+str(layer)
        body = {layer_key: {}}
        body[layer_key][side] = {}
        body[layer_key][side][position] = {}
        if red is not None:
            body[layer_key][side][position]['r'] = red
        if green is not None:
            body[layer_key][side][position]['g'] = green
        if blue is not None:
            body[layer_key][side][position]['b'] = blue

        self.ws_post('/cached', body=body)