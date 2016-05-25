#!/usr/bin/env python
# -*- coding: utf-8 -*-

def main(**kwargs):
    """Main entry point.
    you-get (legacy)
    """
    from .common import main
    try:
        main()
    except KeyboardInterrupt:
        print()
        print('Interrupted by Ctrl-C')

if __name__ == '__main__':
    main()
