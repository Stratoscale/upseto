all: test check_convention

clean:
	rm -fr build dist upseto.egg-info

test:
	PYTHONPATH=$(PWD) python upseto/tests/test.py

check_convention:
	pep8 . --max-line-length=109

install:
	-sudo pip uninstall upseto
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
