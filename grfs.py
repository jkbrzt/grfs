#!/usr/bin/env python
"""
Read-only FUSE filesystem for accessing media on the Ricoh GRII
camera over WiFi.

"""
import logging
import os
import sys
from copy import deepcopy
from stat import S_IFDIR, S_IFREG
from datetime import datetime
from tempfile import TemporaryFile
from functools import reduce

import requests
from fuse import FUSE, Operations, ENOENT, FuseOSError
from requests.adapters import HTTPAdapter


logger = logging.getLogger('grfs')


class GRFS(Operations):

    def __init__(self, client):
        self._client = client
        self._model = Model(client)
        self._download_cache = {}
        self._model.reload()

    def clear_download_cache(self):
        for f in self._download_cache.values():
            os.unlink(f)

    def readdir(self, path, fh):
        logger.info('readdir path=%r fh=%r', path, fh)
        directory = self._model.get(path)
        return ['.', '..'] + list(directory.keys())

    def getattr(self, path, fh=None):
        return self._model.get_attrs(path)

    def read(self, path, size, offset, fh):

        if path not in self._download_cache:
            url = self._model.get(path)['url']
            f = TemporaryFile(prefix='GRFS_')
            f.write(self._client.get_photo(url).content)
            self._download_cache[path] = f

        f = self._download_cache[path]
        f.seek(offset)

        return f.read(size)


class Model:

    def __init__(self, client):
        self.client = client
        self.photos = {}
        self.tree = {}

    def reload(self):
        self.load_from_camera()
        self.build_directory_tree()

    def get(self, path):
        parts = path.strip('/').split('/')
        if parts == ['']:
            return self.tree
        try:
            return reduce(lambda tree, subpath: tree[subpath],
                          parts, self.tree)
        except KeyError:
            raise FuseOSError(ENOENT)

    def get_attrs(self, path):
        logger.info('get attrs %s', path)
        obj = self.get(path)
        if 'url' not in obj:
            return {
                'st_mode': S_IFDIR | 0o755,
                'st_nlink': 2
            }
        attrs = obj['attrs']
        if 'st_size' not in attrs:
            attrs['st_size'] = self.client.get_photo_size(obj['url'])
        return attrs

    def load_from_camera(self):
        self.photos.clear()
        response = self.client.get_objs()['dirs']
        for directory in response:
            self.photos[directory['name']] = files = {}
            for file in directory['files']:
                dt = datetime.strptime(file['d'], '%Y-%m-%dT%H:%M:%S')
                timestamp = int(dt.strftime('%s'))
                filename = file['n']
                path = directory['name'] + '/' + filename
                files[filename] = {
                    'path': path,
                    'url': self.client.get_photo_url(path),
                    'attrs': {
                        'st_mode': S_IFREG | 0o755,
                        'st_nlink': 2,
                        'st_mtime': timestamp,
                        'st_ctime': timestamp,
                    }
                }

    def build_directory_tree(self):
        self.tree.clear()
        sizes = ['thumb', 'view', 'full']
        for size in sizes:
            self.tree[size] = {}
            for dirname, photos in self.photos.items():
                self.tree[size][dirname] = {}
                for filename, photo in photos.items():
                    photo = deepcopy(photo)
                    photo['url'] = '{}?size={}'.format(photo['url'], size)
                    self.tree[size][dirname][filename] = photo


class GRClient:
    """HTTP API client"""

    root = 'http://192.168.0.1'

    def __init__(self):
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=20)
        self.session.mount(self.root, adapter)

    def request(self, method, url, **kwargs):
        if not url.startswith(self.root):
            url = self.root + url
        logger.info('%s %s', method, url)
        return self.session.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def ping(self):
        return self.get('/v1/ping').json()

    def get_device(self):
        return self.get('/v1/constants/device').json()

    def get_objs(self):
        return self.get('/_gr/objs').json()

    def get_photo(self, path, **kwargs):
        if not path.startswith(self.root):
            url = self.get_photo_url(path)
        else:
            url = path
        return self.get(url, stream=True, **kwargs)

    def get_photo_url(self, path):
        return self.root + '/v1/photos/' + path

    def get_photo_size(self, path):
        r = self.get_photo(path, timeout=1)
        return int(r.headers['Content-Length'])


def mount(mountpoint):
    client = GRClient()
    try:
        logger.info('Getting camera info')
        device = client.get_device()
    except:
        logger.error('Unable connect to the camera')
    else:
        for key in sorted(device.keys()):
            logger.info('%s: %s', key, device[key])

    grfs = GRFS(client)
    try:
        FUSE(grfs, mountpoint, foreground=True, nothreads=True, ro=True)
    finally:
        grfs.clear_download_cache()


def main(argv=sys.argv):
    if len(argv) != 2:
        logger.error('usage: %s <mountpoint>' % argv[0])
        exit(1)
    logging.basicConfig(level=logging.DEBUG)
    mount(mountpoint=argv[1])


if __name__ == '__main__':
    main()
