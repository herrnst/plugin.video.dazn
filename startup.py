# -*- coding: utf-8 -*-

from kodi_six import xbmcaddon

addon = xbmcaddon.Addon()

if __name__ == '__main__':
    addon.setSetting('startup', 'true')
