Help on OpenRetina
==================


Install openRetina libraries open python
----------------------------------------

1. Make sure you removed .egg files in /usr/local/… :
 rm -fr  /usr/local/lib/python3.5/site-packages/openRetina-0.1-py3.5.egg
rm -fr  /usr/local/lib/python2.7/site-packages/openRetina-0.1-py2.7.egg

2. Make sure you removed the /built and /dist folder in openRetina :
rm -fr build dist 

3. In the openRetina folder, where the setup.py file is located, execute :
pip3 install -e . 