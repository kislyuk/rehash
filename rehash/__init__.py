from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys, hashlib, base64, zlib
from ctypes import cast, memmove, POINTER, c_void_p
from .structs import EVPobject

opaque_repr = False

class ResumableHasher(object):
    name = None
    _algorithms_guaranteed = getattr(hashlib,
                                     "algorithms_guaranteed",
                                     ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"])

    def __init__(self, name=None, data=None, state=None):
        if state is not None:
            if not self.name:
                raise Exception('Parameter "name" is required')
            self.__setstate__(state=dict(name=name, md_data=zlib.decompress(base64.b64decode(state))))
            if data is not None:
                self.update(data)
            return
        if self.name is not None:
            data = name
        else:
            self.name = name
        if not self.name:
            raise Exception('Parameter "name" is required')
        hasher_args = [] if data is None else [data]
        self._hasher = self._get_hashlib_hasher(self.name)(*hasher_args)

    def _get_hashlib_hasher(self, name):
        if name.startswith("blake2"):
            raise Exception("blake2 algorithms are not OpenSSL-based and not supported by rehash")
        if name.startswith("sha3"):
            raise Exception("sha3 algorithms are not supported by rehash")
        if name.startswith("shake"):
            raise Exception("shake algorithms are not supported by rehash")
        if name in self._algorithms_guaranteed:
            return getattr(hashlib, name)
        else:
            return hashlib.new(name)

    def _get_evp_md_ctx(self):
        c_evp_obj = cast(c_void_p(id(self._hasher)), POINTER(EVPobject))
        if hasattr(c_evp_obj.contents.ctx, "contents"):
            return c_evp_obj.contents.ctx.contents
        else:
            return c_evp_obj.contents.ctx

    def __getstate__(self):
        ctx = self._get_evp_md_ctx()
        ctx_size = ctx.digest.contents.ctx_size
        hasher_state = ctx.md_data[:ctx_size]
        return dict(name=self.name, md_data=hasher_state)

    def __setstate__(self, state):
        self.name = state["name"]
        self._hasher = self._get_hashlib_hasher(self.name)()
        ctx = self._get_evp_md_ctx()
        ctx_size = ctx.digest.contents.ctx_size
        memmove(ctx.md_data, state["md_data"], ctx_size)

    def __getattr__(self, a):
        return getattr(self._hasher, a)

    def __repr__(self):
        if opaque_repr:
            return "{}.{}()".format(self.__module__, self.__class__.__name__)
        else:
            md_data = base64.b64encode(zlib.compress(self.__getstate__()["md_data"])).decode()
            return "{}.{}(state='{}')".format(self.__module__, self.name, md_data)


new = ResumableHasher

def _initialize():
    module = sys.modules[__name__]
    for name in ResumableHasher._algorithms_guaranteed:
        if name.startswith("blake2") or name.startswith("sha3") or name.startswith("shake"):
            continue
        setattr(module, name, type(name, (ResumableHasher,), dict(name=name)))


_initialize()
