Rehash: Resumable Hashlib
=========================

Rehash is a resumable interface to the OpenSSL-based hashers (message digest objects) in the
CPython ``hashlib`` standard library. Rehash provides hashers that
can be pickled, persisted and reconstituted from their ``repr()``,
and otherwise serialized. The rest of the Rehash API is identical to
``hashlib``.

Rehash hashers can be used to checkpoint and restore progress
when hashing large byte streams:

.. code-block:: python

  import pickle, rehash
  hasher = rehash.sha256(b"foo")
  state = pickle.dumps(hasher)

  hasher2 = pickle.loads(state)
  hasher2.update(b"bar")

  assert hasher2.hexdigest() == rehash.sha256(b"foobar").hexdigest()

Installation
------------
::

    pip install rehash

Applications
~~~~~~~~~~~~
Rehash is useful in any situation when your VM is short-lived or preemptable, and the object you're hashing is huge. For
example, Rehash can be used to hand off the hashing state of large objects between AWS Lambda functions or Google Cloud
Functions, which have runtime limits of 5 and 9 minutes, respectively (TODO: example).

.. admonition:: Non-openssl hashers

  ``sha3`` and ``blake2`` hash algorithms in Python 3.6 are not OpenSSL-based and not supported by rehash.

.. admonition:: PyPy

  PyPy uses its own hasher implementations. Those are not serializable using rehash.

.. admonition:: Security note

  By default, rehash objects present themselves with a ``repr()`` that exposes their internal state. This allows one to
  resume the hashing from the point where it stopped. If exposed through an untrusted channel under specific conditions,
  this could potentially allow an attacker to use an extension attack. If you are unsure about the implications of this,
  set ``rehash.opaque_repr = True`` after importing rehash.

Links
-----
* `Project home page (GitHub) <https://github.com/kislyuk/rehash>`_
* `Documentation (Read the Docs) <https://rehash.readthedocs.io/en/latest/>`_
* `Package distribution (PyPI) <https://pypi.python.org/pypi/rehash>`_
* `Change log <https://github.com/kislyuk/rehash/blob/master/Changes.rst>`_

Bugs
~~~~
Please report bugs, issues, feature requests, etc. on `GitHub <https://github.com/kislyuk/rehash/issues>`_.

License
-------
Licensed under the terms of the `Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_.

.. image:: https://travis-ci.org/kislyuk/rehash.png
        :target: https://travis-ci.org/kislyuk/rehash
.. image:: https://codecov.io/github/kislyuk/rehash/coverage.svg?branch=master
        :target: https://codecov.io/github/kislyuk/rehash?branch=master
.. image:: https://img.shields.io/pypi/v/rehash.svg
        :target: https://pypi.python.org/pypi/rehash
.. image:: https://img.shields.io/pypi/l/rehash.svg
        :target: https://pypi.python.org/pypi/rehash
.. image:: https://readthedocs.org/projects/rehash/badge/?version=latest
        :target: https://rehash.readthedocs.org/
