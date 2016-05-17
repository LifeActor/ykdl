#!/usr/bin/env python
# This file is Python 2 compliant.

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
