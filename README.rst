**Rehash** is a resumable interface to the OpenSSL-based hashers in
 the CPython ``hashlib`` standard library. **Rehash** provides hashers
 that can be pickled, reconstituted from their ``repr()``, and
 otherwise serialized. The rest of the **Rehash** API is identical to
 ``hashlib``.

**Rehash** hashers can be used to checkpoint and restore progress
when hashing large byte streams::

  import pickle, rehash
  hasher = rehash.sha256(b"foo")
  state = pickle.dumps(hasher)

  hasher2 = pickle.loads(state)
  hasher2.update(b"bar")

  assert hasher2.hexdigest() == rehash.sha256(b"foobar").hexdigest()
  
Note: sha3, blake2b, blake2s in python 3.6 are not openssl-based and not supported by rehash.

Note: PyPy uses its own hasher implementations. Those are not serializable using rehash.
