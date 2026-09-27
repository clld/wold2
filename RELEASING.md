# Releasing the WOLD clld app

Install from github:
```shell
git clone https://github.com/clld/wold2
cd wold2
pip install -e .[test]
```

Recreate the database:
```shell
clld initdb development.ini --cldf ../wold/cldf/cldf-metadata.json --glottolog ../../glottolog/glottolog
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
pg_dump -xO wold2 > wold2.sql
zip wold2.sql.zip wold2.sql
rm wold2.sql
```

