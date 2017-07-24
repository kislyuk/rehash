#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys, unittest, tempfile, json, logging, pickle, hashlib, ssl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # noqa

import rehash

print("OpenSSL version:", ssl.OPENSSL_VERSION)

class TestResumableHasher(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level="DEBUG")

    def assert_resumable(self, hasher):
        hasher.update(b"foo")
        state = pickle.dumps(hasher)
        hasher2 = pickle.loads(state)
        hasher.update(b"bar"*1024*1024)
        hasher2.update(b"bar"*1024*1024)
        self.assertEqual(hasher.digest(), hasher2.digest())

    def test_basic_statements(self):
        for algorithm in hashlib.algorithms_guaranteed:
            if algorithm.startswith("blake2") or algorithm.startswith("sha3") or algorithm.startswith("shake"):
                with self.assertRaises(Exception):
                    rehash.ResumableHasher(algorithm.lower())
            else:
                print(algorithm)
                self.assert_resumable(rehash.new(algorithm.lower()))
                self.assert_resumable(rehash.new(algorithm.lower(), b"initial_data"))
                self.assert_resumable(rehash.ResumableHasher(algorithm.lower()))
                self.assert_resumable(rehash.ResumableHasher(algorithm.lower(), b"initial_data"))
                self.assert_resumable(getattr(rehash, algorithm)())
                self.assert_resumable(getattr(rehash, algorithm)(b"initial_data"))

    def test_repr(self):
        # Some of the memory at the tail of the hasher state is uninitialized at initial state
        self.assertEqual(
            repr(rehash.sha256())[:64],
            "rehash.sha256(state='eJxLf8aZ1boufXfR5zwbq6/+S+uD+AJ7Mlhnr77ZLC959kE0AxWBAhDfa7Ku5N63OAIAWHETSw==')"[:64]
        )
        rehash.opaque_repr = True
        self.assertEqual(
            repr(rehash.sha256()),
            "rehash.sha256()"
        )

    def test_doc_example(self):
        import pickle, rehash
        hasher = rehash.sha256(b"foo")
        state = pickle.dumps(hasher)

        hasher2 = pickle.loads(state)
        hasher2.update(b"bar")

        assert hasher2.hexdigest() == rehash.sha256(b"foobar").hexdigest()

if __name__ == '__main__':
    unittest.main()
