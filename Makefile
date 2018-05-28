.PHONY: test
test: test/python3 test/python2

.PHONY: test/python3
test/python3:
	python3 test_dfcompare.py

.PHONY: test/python2
test/python2:
	python2 test_dfcompare.py

.PHONY: docs
docs:
	sphinx-build docs docs/.build
