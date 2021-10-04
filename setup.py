from setuptools import setup, find_packages


setup(
    name='wold2',
    version='0.0',
    description='wold',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    author='Robert Forkel, MPI SHH',
    author_email='forkel@shh.mpg.de',
    url='http://wold.clld.org',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='wold2',
    install_requires=[
        'clld>=8',
        'clldmpg>=4.2',
        'sqlalchemy',
        'waitress',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox'
        ],
        'test': [
            'mock',
            'psycopg2',
            'pytest>=3.1',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    entry_points="""\
      [paste.app_factory]
      main = wold2:main
      [console_scripts]
      initialize_wold_db = wold2.scripts.initializedb:main
      """)
