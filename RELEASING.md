# Releasing the WOLD clld app

Install from github:
```shell
git clone --branch v4.2 --depth 1 https://github.com/lexibank/wold
git clone --branch v5.3 --depth 1 https://github.com/glottolog/glottolog
git clone https://github.com/clld/wold2
cd wold2
pip install -e .[test]
```

Recreate the database:
```shell
clld initdb development.ini --cldf ../wold/cldf/cldf-metadata.json --glottolog ../glottolog
```

Run the test suite:
```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO --compress gzip:9 wold2 > wold2.sql.gz
```

