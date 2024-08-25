YouKuDownLoader
===============

.. image:: https://img.shields.io/pypi/v/ykdl.svg
   :target: https://pypi.python.org/pypi/ykdl


A video downloader focus on China mainland video sites.

Origin website: https://github.com/zhangn1985/ykdl
Later migrated to a new website: https://github.com/SeaHOH/ykdl
Today it migrated to my name, and this is the new website: https://github.com/LifeActor/ykdl

This project is a fork of
`you-get <https://github.com/soimort/you-get>`_ with below changes.

- Structured source code.
- Focus on China mainland video sites.
- Dropped supports of Python 3.4 and below
  (see `#487 <https://github.com/SeaHOH/ykdl/issues/487>`_).

Simple installation guide
-------------------------

There are some useful software package managers.

- **macOS/Linux**: `Homebrew <https://brew.sh/>`_
- **Debian/Linux**: APT
- **Windows**: `Chocolatey <https://chocolatey.org/install>`_

Step:
 0. Dependencies

    | `FFmpeg <https://ffmpeg.org/>`_, for merge media files.
    | `mpv <https://mpv.io/>`_, default media player (optimal compatibility).

 #. `Python 3 <https://www.python.org/downloads/>`_

 #. pip and setuptools, make sure they are updated.

    .. code-block:: console

        python3 -m ensurepip
        python3 -m pip install pip --upgrade
        python3 -m pip install setuptools --upgrade

 #. ykdl from PyPI or GitHub

    .. code-block:: console

        pip3 install ykdl --upgrade

    .. code-block:: console

        pip3 install https://github.com/SeaHOH/ykdl/archive/master.zip --force-reinstall --no-deps
        pip3 install https://github.com/SeaHOH/ykdl/archive/master.zip --upgrade

 #. Make sure those folders are in your **PATH**, if they are not, add them.

    | **Windows**: folders of ffmpeg.exe, mpv.exe, and python.exe,
                   and folder "<**PYTHONHOME**>\\Scripts"
    | **others**: "~/.local/bin" or "/usr/local/bin"

Site status
-----------

Please check wiki page:
`sites-status <https://github.com/SeaHOH/ykdl/wiki/sites-status>`_

Bugs report, features require, and pull requests are welcome.

Project Ownership Transition
----------------------------

I am pleased to announce that I have taken over the ownership of the YouKuDownLoader project from @SeaHOH today. This transition marks the beginning of an exciting new chapter for the project, and I am committed to ensuring its continued development and success.

### Future Plans

- **Enhanced Features**: I plan to introduce new features that will improve the user experience and expand the capabilities of the downloader.
- **Regular Updates**: Regular updates will be pushed to ensure compatibility with the latest video sites and technologies.
- **Community Engagement**: I will actively engage with the community to gather feedback and suggestions for future enhancements.
- **Bug Fixes**: Addressing existing bugs and issues to ensure a smooth and reliable user experience.

Your support and contributions are invaluable to the project's success. Together, we can make YouKuDownLoader an even more powerful tool for downloading videos from China mainland video sites.

Thank you for your continued support!

---

*Note: For any inquiries or suggestions, please feel free to open an issue or reach out directly.*
