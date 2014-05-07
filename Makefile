all: test check_convention

clean:
	rm -fr build dist upseto.egg-info

test:
	PYTHONPATH=$(PWD) python upseto/tests/test.py

check_convention:
	pep8 . --max-line-length=109

uninstall:
	sudo pip uninstall upseto
	sudo rm /usr/bin/upseto

install:
	-sudo pip uninstall upseto
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
	sudo cp upseto.sh /usr/bin/upseto
	sudo chmod 755 /usr/bin/upseto
