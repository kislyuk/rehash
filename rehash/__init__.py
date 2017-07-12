from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys, hashlib
from ctypes import cast, c_void_p, POINTER, Structure, c_int, c_ulong, c_char, c_size_t, c_ssize_t, py_object, memmove
from ssl import OPENSSL_VERSION

PyObject_HEAD = [
    ('ob_refcnt', c_size_t),
    ('ob_type', c_void_p)
]

# OpenSSL 1.0.2 and earlier:
# https://github.com/openssl/openssl/blob/OpenSSL_1_0_2-stable/crypto/evp/evp.h#L159-L181
# OpenSSL 1.1.0 and later:
# https://github.com/openssl/openssl/blob/master/crypto/include/internal/evp_int.h#L99-L113
class EVP_MD(Structure):
    _fields_ = [
        ('type', c_int),
        ('pkey_type', c_int),
        ('md_size', c_int),
        ('flags', c_ulong),
        ('init', c_void_p),
        ('update', c_void_p),
        ('final', c_void_p),
        ('copy', c_void_p),
        ('cleanup', c_void_p),
    ]
    if OPENSSL_VERSION < "OpenSSL 1.1.0":
        _fields_ += [
            ('sign', c_void_p),
            ('verify', c_void_p),
            ('required_pkey_type', c_int * 5),
        ]
    _fields_ += [
        ('block_size', c_int),
        ('ctx_size', c_int),
    ]

# https://github.com/openssl/openssl/blob/master/crypto/evp/evp_locl.h#L12-L22
class EVP_MD_CTX(Structure):
    _fields_ = [
        ('digest', POINTER(EVP_MD)),
        ('engine', c_void_p),
        ('flags', c_ulong),
        ('md_data', POINTER(c_char)),
    ]

class EVPWrapper(Structure):
    _fields_ = PyObject_HEAD + [
        ("name", POINTER(py_object)),
        ("ctx", POINTER(EVP_MD_CTX))
    ]

class ResumableHasher(object):
    name = None

    def __init__(self, name=None, data=None):
        if self.name is not None:
            data = name
        else:
            self.name = name
        hasher_args = [] if data is None else [data]
        self._hasher = self._get_hashlib_hasher(self.name)(*hasher_args)

    def _get_hashlib_hasher(self, name):
        if name.startswith("blake2"):
            raise Exception("blake2 algorithms are not OpenSSL-based and not supported by rehash")
        if name.startswith("sha3"):
            raise Exception("sha3 algorithms are not supported by rehash")
        if name.startswith("shake"):
            raise Exception("shake algorithms are not supported by rehash")
        if name in hashlib.algorithms_guaranteed:
            return getattr(hashlib, name)
        else:
            return hashlib.new(name)

    def _get_evp_md_ctx(self):
        c_evp_obj = cast(c_void_p(id(self._hasher)), POINTER(EVPWrapper))
        return c_evp_obj.contents.ctx.contents

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

def _initialize():
    module = sys.modules[__name__]
    for name in hashlib.algorithms_guaranteed:
        if name.startswith("blake2"):
            continue
        setattr(module, name, type(name, (ResumableHasher,), dict(name=name)))


_initialize()
