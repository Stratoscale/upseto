all: unittest check_convention

clean:
	rm -fr build dist upseto.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=upseto/*.py
unittest:
	rm -f .coverage*
	PYTHONPATH=`pwd` COVERAGE_FILE=`pwd`/.coverage coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	coverage combine
	coverage report --show-missing --rcfile=coverage.config --fail-under=86 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall upseto
	-sudo rm /usr/lib/python2.7/site-packages/upseto.pth
	sudo rm /usr/bin/upseto

install:
	-yes | sudo pip uninstall upseto
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
	sudo cp upseto.pth /usr/lib/python2.7/site-packages/upseto.pth
	sudo cp upseto.sh /usr/bin/upseto
	sudo chmod 755 /usr/bin/upseto
