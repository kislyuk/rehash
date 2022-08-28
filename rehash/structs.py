from ssl import OPENSSL_VERSION
from sys import version_info as PYTHON_VERSION
from ctypes import c_void_p, POINTER, Structure, c_int, c_ulong, c_char, c_size_t, c_ssize_t, py_object

PyObject_HEAD = [
    ('ob_refcnt', c_size_t),
    ('ob_type', c_void_p)
]

# OpenSSL struct evp_md_st
# OpenSSL 1.0.2 and earlier:
# https://github.com/openssl/openssl/blob/OpenSSL_1_0_2-stable/crypto/evp/evp.h#L159-L181
# OpenSSL 1.1.0:
# https://github.com/openssl/openssl/blob/OpenSSL_1_1_0-stable/crypto/include/internal/evp_int.h#L88-L102
# OpenSSL 1.1.1 and later:
# https://github.com/openssl/openssl/blob/master/include/crypto/evp.h#L247-L288
class EVP_MD(Structure):
    _fields_ = [
        ('type', c_int),
        ('pkey_type', c_int),
        ('md_size', c_int),
        ('flags', c_ulong),
    ]
    if OPENSSL_VERSION >= "OpenSSL 3.0.0":
        _fields_ += [
            ('origin', c_int),
        ]
    _fields_ += [
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

# OpenSSL struct evp_md_ctx_st
# OpenSSL 1.1.0 and earlier:
# https://github.com/openssl/openssl/blob/master/crypto/evp/evp_locl.h#L12-L22
# OpenSSL 1.1.1 and later, before 3.0.0:
# https://github.com/openssl/openssl/blob/OpenSSL_1_1_1-stable/crypto/evp/evp_local.h#L12-L22
# OpenSSL 3.0.0 and later:
# https://github.com/openssl/openssl/blob/master/crypto/evp/evp_local.h#L16-L34
class EVP_MD_CTX(Structure):
    _fields_ = [
        ('digest', POINTER(EVP_MD)),
        ('engine', c_void_p),
        ('flags', c_ulong),
        ('md_data', POINTER(c_char)),
    ]
    if OPENSSL_VERSION >= "OpenSSL 3.0.0":
        _fields_ = [
            ('reqdigest', POINTER(EVP_MD)),
        ] + _fields_ + [
            ('pctx', c_void_p),
            ('update', c_void_p),
            ('algctx', c_void_p),
            ('fetched_digest', POINTER(EVP_MD)),
        ]

# Python 3.8+: https://github.com/python/cpython/blob/master/Modules/_hashopenssl.c#L58-L64
# Python 3.5.3 - 3.7: https://github.com/python/cpython/blob/3.7/Modules/_hashopenssl.c#L52-L59
# Python 3 - 3.5.2: https://github.com/python/cpython/blob/3.4/Modules/_hashopenssl.c#L39-L46
# Python 2.7.13+: https://github.com/python/cpython/blob/2.7/Modules/_hashopenssl.c#L71-L78
class EVPobject(Structure):
    _fields_ = PyObject_HEAD + (
        [("name", POINTER(py_object))] if PYTHON_VERSION < (3, 8) else []
    ) + [
        ("ctx", EVP_MD_CTX if (3, 0) < PYTHON_VERSION < (3, 5, 3) or PYTHON_VERSION < (2, 7, 13) else POINTER(EVP_MD_CTX))
    ]
