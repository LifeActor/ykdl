YouKuDownLoader
===============

.. image:: https://img.shields.io/github/v/release/zhangn1985/ykdl.svg
   :target: https://github.com/zhangn1985/ykdl/releases
.. image:: https://img.shields.io/pypi/v/ykdl.svg
   :target: https://pypi.python.org/pypi/ykdl
.. image:: https://travis-ci.org/zhangn1985/ykdl.svg
   :target: https://travis-ci.org/zhangn1985/ykdl


A video downloader focus on China mainland video sites.

website: https://github.com/zhangn1985/ykdl

This project is a fork of `you-get <https://github.com/soimort/you-get>`_ with below changes.

1. Structured source code.
2. focus on China mainland video sites.
3. dropped supports of Python 3.4 and below (see `#487 <https://github.com/zhangn1985/ykdl/issues/487>`_).

Simple installation guide
-------------------------

Packages on PyPI had been outdated, consider install via other package managers, or direct install from source.

macOS/Linux
^^^^^^^^^^^

0. install Homebrew

.. code-block:: console

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

1. install FFmpeg and mpv [**optional**]

.. code-block:: console

    brew install ffmpeg mpv

2. install ykdl (v1.7.0)

.. code-block:: console

    brew install ykdl

3. **/usr/local/bin** is already in your PATH, if it is not, add it

Debian/Linux
^^^^^^^^^^^^

1. install FFmpeg and mpv [**optional**]

.. code-block:: console

    sudo apt-get install ffmpeg mpv

2. install pip

.. code-block:: console

    sudo apt-get install python3-pip

3. install ykdl

.. code-block:: console

    pip3 install git+https://github.com/zhangn1985/ykdl.git --upgrade --user

4. add **~/.local/bin** to your PATH

Windows 10
^^^^^^^^^^

0. install Chocolatey with PowerShell

.. code-block:: console

    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

1. install FFmpeg and mpv [**optional**]

.. code-block:: console

    choco install ffmpeg mpv

2. install Python (**--version** is not necessary, default to newest version)

.. code-block:: console

    choco install python --version=3.x.x

3. install pip

.. code-block:: console

    python3.x -m ensurepip
    python3.x -m pip install pip --upgrade
    python3.x -m pip install setuptools --upgrade

4. install ykdl

.. code-block:: console

    pip3 install git+https://github.com/zhangn1985/ykdl.git --upgrade

Windows 7+
^^^^^^^^^^

1. install `FFmpeg <https://ffmpeg.org/download.html#build-windows>`_ and `mpv <https://mpv.io/>`_ [**optional**]

2. install Python 3 from `python.org <https://www.python.org/>`_

3. make sure folders of ffmpeg.exe, mpv.exe, python.exe and folder python/Scripts are in your PATH

4. install pip and ykdl, same as Windows 10, see above

Other OS
^^^^^^^^

Please DIY.


Site status
-----------

Please check wiki page: `sites-status <https://github.com/zhangn1985/ykdl/wiki/sites-status>`_

File bugs or requirements are welcome.

Submit PRs are welcome.
