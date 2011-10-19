try:
    from setuptools import setup
except ImportError:
    fomr distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Gordon McNutt',
    'url' : 'URL to get it at',
    'download_url': 'Where to download it.',
    'author_email': 'gmcnutt@cableone.net',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['azoth'],
    'scripts': [],
    'name': 'projectname'
}

setup(**config)
