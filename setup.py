try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Single-player RPG game',
    'author': 'Gordon McNutt',
    'url' : 'URL to get it at',
    'download_url': 'Where to download it.',
    'author_email': 'gmcnutt@cableone.net',
    'version': '0.1',
    'install_requires': ['nose', 'pygame'],
    'packages': ['azoth'],
    'scripts': [],
    'name': 'azoth'
}

setup(**config)
