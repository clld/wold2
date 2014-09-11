The World Loanword Database (WOLD)
==================================

Cite
----

WOLD is licensed under a Creative Commons Attribution 3.0 Unported License. Cite as

  Haspelmath, Martin & Tadmor, Uri (eds.) 2009.
  World Loanword Database.
  Leipzig: Max Planck Institute for Evolutionary Anthropology.
  (Available online at http://wold.clld.org) 
  [![DOI](https://zenodo.org/badge/5142/clld/wold2.png)](http://dx.doi.org/10.5281/zenodo.11137)


Install
-------

To get WOLD running locally, you need python 2.7 and have to run your system's equivalent to the following bash commands:

```bash
virtualenv --no-site-packages wold
cd wold/
. bin/activate
curl -O http://zenodo.org/record/11137/files/wold2-v2009.zip
unzip wold2-v2009.zip
python clld-wold2-dbe8bcf/fromdump.py
cd wold2/
pip install -r requirements.txt
python setup.py develop
python wold2/scripts/unfreeze.py sqlite.ini
pserve sqlite.ini
```

Then you should be able to access the application by visiting http://localhost:6543 in your browser. Note that you still need an internet connection for the application to download external resources like the map tiles or javascript libraries.
