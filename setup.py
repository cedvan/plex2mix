from setuptools import setup, find_packages

setup(
    name='plex2mix',
    version='1.0.1',
    packages=find_packages(),
    description='Python cli utility to download Plex playlists.',
    author='Cedvan',
    author_email='contact@cedvan.com',
    url='https://github.com/cedvan/plex2mix',
    include_package_data=True,
    install_requires=[
        'Click',
        'click-aliases',
        'PlexAPI',
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'plex2mix = plex2mix.main:cli',
        ],
    },
)
