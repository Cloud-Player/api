from setuptools import setup, find_packages


setup(
    name='cloudplayer.api',
    version='0.2.0.dev0',
    author='Nicolas Drebenstedt',
    author_email='hello@cloud-player.io',
    url='https://cloud-player.io',
    description='REST API for Cloud-Player',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='Apache-2.0',
    namespace_packages=['cloudplayer'],
    setup_requires=['setuptools_git'],
    install_requires=[
        'psycopg2',
        'pycurl',
        'PyJWT',
        'redis',
        'setuptools',
        'sqlalchemy',
        'tornado'
    ],
    extras_require={
        'test': [
            'mock',
            'pylint',
            'pytest-pep8',
            'pytest-postgresql',
            'pytest-redis',
            'pytest-timeout',
            'pytest-tornado',
            'pytest'
        ]
    },
    entry_points={
        'console_scripts': [
            'api=cloudplayer.api.app:main',
            'pytest=pytest:main [test]',
            'test=pytest:main [test]'
        ]
    }
)
