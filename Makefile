test: clean
	tox
	coverage combine
	coverage report
	coverage html

clean:
	rm -f .coverage.*
	rm -rf htmlcov
	coverage erase

.PHONY: test clean
