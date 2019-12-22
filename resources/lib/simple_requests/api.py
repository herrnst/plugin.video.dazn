from __future__ import unicode_literals
__author__ = 'bromix'

import sys
if (sys.version_info[0] == 2):
    from urllib2 import build_opener, HTTPDefaultErrorHandler, HTTPError, HTTPRedirectHandler, HTTPSHandler, Request
    from urllib import addinfourl, quote, urlencode
    from StringIO import StringIO
else:
    from urllib.request import build_opener, HTTPDefaultErrorHandler, HTTPRedirectHandler, HTTPSHandler, Request
    from urllib.response import addinfourl
    from urllib.parse import quote, urlencode
    from urllib.error import HTTPError
    from io import StringIO
import gzip
from kodi_six.utils import py2_decode, py2_encode

import json as real_json


class ErrorHandler(HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        infourl = addinfourl(fp, hdrs, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl


class NoRedirectHandler(HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class Response():
    def __init__(self):
        self.headers = {}
        self.code = -1
        self.text = u''
        self.status_code = -1

    def read(self):
        return self.text

    def json(self):
        # ensure json loads str
        s = self.text
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return real_json.loads(s)

    # py2 get lowercase, py3 no
    def header(self, header, default=''):
        return self.headers.get(header, self.headers.get(header.lower(), default))

def _request(method, url,
             params=None,
             data=None,
             headers=None,
             cookies=None,
             files=None,
             auth=None,
             timeout=None,
             allow_redirects=True,
             proxies=None,
             hooks=None,
             stream=None,
             verify=None,
             cert=None,
             json=None):
    if not headers:
        headers = {}

    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")

    handlers = []

    import sys
    # starting with python 2.7.9 urllib verifies every https request
    if False == verify and sys.version_info >= (2, 7, 9):
        import ssl

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        handlers.append(HTTPSHandler(context=ssl_context))

    # handlers.append(HTTPCookieProcessor())
    # handlers.append(ErrorHandler)
    if not allow_redirects:
        handlers.append(NoRedirectHandler)
    opener = build_opener(*handlers)

    query = ''
    if params:
        for key in params:
            value = params[key]
            if isinstance(value, str):
                value = py2_decode(value)
            params[key] = py2_decode(value)
        query = urlencode(params)
    if query:
        url += '?%s' % query
    request = Request(url)
    if headers:
        for key in headers:
            request.add_header(key, headers[key])
    if data or json:
        if headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded') and data:
            # transform a string into a map of values
            if isinstance(data, basestring):
                _data = data.split('&')
                data = {}
                for item in _data:
                    name, value = item.split('=')
                    data[name] = value

            # encode each value
            for key in data:
                data[key] = data[key].encode('utf-8')

            # urlencode
            request.data = urlencode(data, 'utf-8')
        elif headers.get('Content-Type', '').startswith('application/json') and data:
            request.data = real_json.dumps(data).encode('utf-8')
        elif json:
            request.data = real_json.dumps(json).encode('utf-8')
        else:
            if not isinstance(data, basestring):
                data = str(data)

            if isinstance(data, str):
                data = data.encode('utf-8')
            request.data = data
    elif method.upper() in ['POST', 'PUT']:
        request.data = "null"
    request.get_method = lambda: method
    result = Response()
    response = None
    try:
        response = opener.open(request)
    except HTTPError as e:
        # HTTPError implements addinfourl, so we can use the exception to construct a response
        if isinstance(e, addinfourl):
            response = e
    except Exception as e:
        result.text = py2_decode(e)
        return result

    # process response
    result.headers.update(response.headers)
    result.status_code = response.getcode()
    if method.upper() == 'HEAD':
        return result
    elif response.headers.get('Content-Encoding', '').startswith('gzip'):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        result.text = py2_decode(f.read())
    else:
        result.text = py2_decode(response.read())

    return result


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return _request('GET', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return _request('POST', url, data=data, json=json, **kwargs)


def put(url, data=None, json=None, **kwargs):
    return _request('PUT', url, data=data, json=json, **kwargs)


def delete(url, **kwargs):
    return _request('DELETE', url, **kwargs)


def head(url, **kwargs):
    return _request('HEAD', url, **kwargs)