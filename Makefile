all: unittest check_convention

clean:
	rm -fr build dist upseto.egg-info

SITE = python -c "import sys; print sys.path[-1]"

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=upseto/*.py
unittest:
	rm -f .coverage*
	PYTHONPATH=`pwd` COVERAGE_FILE=`pwd`/.coverage python -m coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	python -m coverage combine
	python -m coverage report --show-missing --rcfile=coverage.config --fail-under=86 --include='$(COVERED_FILES)'
	PYTHONPATH=`pwd` python tests/verifyloggingnotusedinjoinnamespaces.py

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall upseto
	-sudo rm $(SITE)/upseto.pth
	-sudo rm /etc/bash_completion.d/upseto.sh
	-sudo rm /usr/bin/upseto


install: uninstall
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo pip install --upgrade ./
