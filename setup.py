from setuptools import setup, find_packages

requires = [
    'clldmpg>=1.0.0',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'mock==1.0',
]

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
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='wold2',
    install_requires=requires,
    tests_require=tests_require,
    entry_points="""\
      [paste.app_factory]
      main = wold2:main
      [console_scripts]
      initialize_wold_db = wold2.scripts.initializedb:main
      """)
