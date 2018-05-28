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

.PHONY: upload
upload:
	rm -rf dfcompare.egg-info dist
	python3 setup.py sdist
	twine upload dist/*
