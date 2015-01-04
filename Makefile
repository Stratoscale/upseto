all: unittest check_convention

clean:
	rm -fr build dist upseto.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=upseto/*.py
unittest:
	rm -f .coverage*
	PYTHONPATH=`pwd` COVERAGE_FILE=`pwd`/.coverage python -m coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	python -m coverage combine
	python -m coverage report --show-missing --rcfile=coverage.config --fail-under=86 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall upseto
	-sudo rm /usr/lib/python2.7/site-packages/upseto.pth /usr/lib/python2.7/dist-packages/upseto.pth
	-sudo rm /etc/bash_completion.d/upseto.sh
	sudo rm /usr/bin/upseto

install:
	-yes | sudo pip uninstall upseto
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo python setup.py install
	if [ -d /usr/lib/python2.7/site-packages ]; then sudo cp upseto.pth /usr/lib/python2.7/site-packages/upseto.pth; else sudo cp upseto.pth /usr/lib/python2.7/dist-packages/upseto.pth; fi
	sudo cp upseto.sh /usr/bin/upseto
	sudo chmod 755 /usr/bin/upseto
	sudo cp bash.completion.sh /etc/bash_completion.d/upseto.sh
