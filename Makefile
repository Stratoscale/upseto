all: test check_convention

test:
	PYTHONPATH=$(PWD)/py python py/upseto/tests/test.py

check_convention:
	pep8 py --max-line-length=109

install:
	echo not implemented yet
	false
