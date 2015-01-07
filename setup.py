from setuptools import setup, find_packages

requires = [
    'clld>=0.15.5',
    'clldmpg',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='wold2',
      version='0.0',
      description='wold',
      long_description='',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='wold2',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = wold2:main
      [console_scripts]
      initialize_wold_db = wold2.scripts.initializedb:main
      """,
      )
