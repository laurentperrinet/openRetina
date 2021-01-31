default: index.html
NAME = openRetina

edit:
	atom setup.py src/__init__.py src/$(NAME).py README.md Makefile requirements.txt

pypi_all: pypi_tags pypi_push pypi_upload pypi_docs
# https://docs.python.org/2/distutils/packageindex.html
pypi_tags:
	git commit -am' tagging for PyPI '
	# in case you wish to delete tags, visit http://wptheming.com/2011/04/add-remove-github-tags/
	git tag 0.1 -m "Adds a tag so that we can put this on PyPI."
	git push --tags origin master

pypi_push:
	python3 setup.py register

pypi_upload:
	python3 setup.py sdist upload

pypi_docs:
	#rm web.zip index.html
	#ipython3 nbconvert --to html $(NAME).ipynb
	#mv $(NAME).html index.html
	#runipy $(NAME).ipynb  --html  index.html
	zip web.zip index.html
	open https://pypi.python.org/pypi?action=pkg_edit&name=$NAME

install_dev:
	pip3 uninstall -y $(NAME) ; pip3 install --user -e .

todo:
	grep -R * (^|#)[ ]*(TODO|FIXME|XXX|HINT|TIP)( |:)([^#]*)

.PHONY: clean
