PYTHON=python3.6

ENV_DIR=.env_$(PYTHON)
IN_ENV=. $(ENV_DIR)/bin/activate &&

TEST_CONTEXT=export TEST_ENV=True &&

env: $(ENV_DIR)

setup:
	$(IN_ENV) python -m pip install -r requirements.txt
	$(IN_ENV) $(PYTHON) -m pip install --editable .

test: setup
	$(IN_ENV) python -m pip install nose coverage
	$(IN_ENV) $(TEST_CONTEXT) python `which nosetests` -q -s tests/ --with-coverage --cover-erase --cover-package=src
	$(IN_ENV) coverage report -m

requirements:
	$(IN_ENV) python -m pip install -r requirements.txt

unify:
	$(IN_ENV) python -m pip install unify
	- $(IN_ENV) unify --in-place --recursive src
