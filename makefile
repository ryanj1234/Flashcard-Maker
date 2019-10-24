.PHONY: install test

default: test

test:
	PYTHONPATH=./ pytest --cov-report html --cov=wikitools test/

clean:
	rm -rf htmlcov .coverage
