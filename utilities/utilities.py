import os
import sys
from importlib.machinery import SourceFileLoader

def get_credentials():
    ''' 
    Returns credentials file from the home dir
    '''
    return SourceFileLoader(
        'credentials',os.path.normpath(os.path.expanduser('~/credentials.py'))).load_module()
