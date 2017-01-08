import os
import sys

def get_credentials():
    """ Returns credentials module from HOME directory; works with Python 2 and 3 """
    # Python 3
    if sys.version_info >= (3,):
        from importlib.machinery import SourceFileLoader, SourcelessFileLoader
        # Try to load source file
        try:
            return SourceFileLoader(
                'credentials',
                os.path.normpath(os.path.expanduser('~/credentials.py'))
            ).load_module()
        # Try to load compiled file
        except FileNotFoundError:
            return SourcelessFileLoader(
                'credentials',
                os.path.normpath(os.path.expanduser('~/credentials35.pyc'))
            ).load_module()
    # Python 2
    else:
        from imp import load_source, load_compiled
        # Try to load source file
        try:
            return load_source(
                u'credentials',
                os.path.normpath(os.path.expanduser(u'~/credentials.py'))
            )
        # Try to load compiled file
        except IOError:
            return load_compiled(
                u'credentials',
                os.path.normpath(os.path.expanduser(u'~/credentials27.pyc'))
            )

