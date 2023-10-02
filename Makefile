all: unittest check_convention

clean:
	rm -fr build dist upseto.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=upseto/*.py
unittest:
	rm -f .coverage*
	PYTHONPATH=`pwd` COVERAGE_FILE=`pwd`/.coverage python2 -m coverage run --append -m unittest $(UNITTESTS)
	python2 -m coverage combine
	python2 -m coverage report --show-missing --rcfile=coverage.config --fail-under=75 --include='$(COVERED_FILES)'
	PYTHONPATH=`pwd` python2 tests/verifyloggingnotusedinjoinnamespaces.py

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-sudo python2 -m pip uninstall -y upseto

install: uninstall
	sudo python2 -m pip install .
