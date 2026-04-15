import os
import posixpath
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryMediaStorage(Storage):
    """Store uploaded media in Cloudinary while keeping Django ImageFields."""

    def _open(self, name, mode='rb'):
        raise NotImplementedError('Cloudinary media files are served by URL only.')

    def _save(self, name, content):
        folder = posixpath.dirname(name).strip('/')
        options = {
            'resource_type': 'image',
            'folder': folder or None,
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
        }
        result = cloudinary.uploader.upload(content, **{k: v for k, v in options.items() if v is not None})
        return result['public_id']

    def delete(self, name):
        public_id = self._normalize_public_id(name)
        if public_id:
            cloudinary.uploader.destroy(public_id, invalidate=True, resource_type='image')

    def exists(self, name):
        return False

    def url(self, name):
        if not name:
            return ''
        if name.startswith('http://') or name.startswith('https://'):
            return name
        return cloudinary_url(name, secure=True, resource_type='image')[0]

    def size(self, name):
        raise NotImplementedError('Cloudinary-managed files do not expose size via Django storage.')

    def _normalize_public_id(self, name):
        if not name:
            return ''
        if name.startswith('http://') or name.startswith('https://'):
            parsed = urlparse(name)
            path = parsed.path
            marker = '/upload/'
            if marker in path:
                public_path = path.split(marker, 1)[1]
                public_path = public_path.split('/', 1)[1] if public_path.startswith('v') and '/' in public_path else public_path
                return os.path.splitext(public_path)[0]
            return ''
        return os.path.splitext(name)[0]
