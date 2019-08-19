# -*- coding: utf-8 -*-

from .client import Client

class Rails:

    def __init__(self, plugin, i):
        self.item = {}
        self.plugin = plugin
        id_ = self.plugin.utfenc(i['Id'])
        self.item['mode'] = 'rail'
        self.item['title'] = self.plugin.get_resource(id_, prefix='browseui_railHeader')
        self.item['id'] = id_
        self.item['plot'] = id_
        if self.plugin.is_valid_uuid(id_):
            rail = Client(self.plugin).rail(id_)
            self.item['title'] = rail.get('Title', False)
            self.item['plot'] = self.item['title']
        else:
            self.item['title'] = self.plugin.get_resource(id_, prefix='browseui_railHeader')
            self.item['plot'] = id_
        #Title ist Text in auf dem Bildschirm
        if i.get('Params', ''):
            self.item['params'] = i['Params']
