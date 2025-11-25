.. _installing.python:

Python library
==============

runixinstall ships on `PyPi <https://pypi.org/>`_ as `runixinstall <pypi.org/project/runixinstall/>`_.
But the library can be installed manually as well.

.. warning::
    These steps are not required if you want to use runixinstall on the official Arch Linux ISO.

Installing with pacman
----------------------

runixinstall is on the `official repositories <https://wiki.archlinux.org/index.php/Official_repositories>`_.
And it will also install runixinstall as a python library.

To install both the library and the runixinstall script:

.. code-block:: console

    pacman -S runixinstall

Alternatively, you can install only the library and not the helper executable using the ``python-runixinstall`` package.

Installing from PyPI
--------------------

The basic concept of PyPI applies using `pip`.

.. code-block:: console

    pip install runixinstall

.. _installing.python.manual:

Install using source code
-------------------------

You can also install using the source code.
For sake of simplicity we will use ``git clone`` in this example.

.. code-block:: console

    git clone https://github.com/archlinux/runixinstall

You can either move the folder into your project and simply do

.. code-block:: python

    import runixinstall

Or you can PyPa's `build <https://github.com/pypa/build>`_ and `installer <https://github.com/pypa/installer>`_ to install it into pythons module path.

.. code-block:: console

    $ cd runixinstall
    $ python -m build .
    $ python -m installer dist/*.whl
