test:
	cd tests; nosetests
clean:
	find . -name '*.pyc' -exec rm -f {} \;
