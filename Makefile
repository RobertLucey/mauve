PYTHON=python3.6

ENV_DIR=.env_$(PYTHON)
IN_ENV=. $(ENV_DIR)/bin/activate &&

TEST_CONTEXT=export TEST_ENV=True && export BOTO_CONFIG=/dev/null &&

MKFILE_DIR_PATH := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

env: $(ENV_DIR)

dependencies:
	apt install calibre

setup: dependencies
	$(PYTHON) -m virtualenv -p $(PYTHON) $(ENV_DIR)
	$(IN_ENV) python -m pip install -r requirements.txt
	$(IN_ENV) $(PYTHON) -m pip install --editable .

test: setup
	$(IN_ENV) python -m pip install nose coverage mock
	$(IN_ENV) $(TEST_CONTEXT) python `which nosetests` -q -s tests/ --with-coverage --cover-erase --cover-package=src
	$(IN_ENV) coverage report -m

quick_test:
	$(IN_ENV) $(TEST_CONTEXT) `which nosetests` --with-coverage --cover-package=mauve --cover-erase
	$(IN_ENV) coverage report -m

requirements:
	$(IN_ENV) python -m pip install -r requirements.txt

unify:
	$(IN_ENV) python -m pip install unify
	- $(IN_ENV) unify --in-place --recursive src

compress_for_later:
	tar cf - /opt/aaa | pv | pigz > $(MKFILE_DIR_PATH)archive.tar.gz

restore_from_gz:
	pigz -dc $(MKFILE_DIR_PATH)archive.tar.gz | pv | tar xf -C / -

download_books:
	test -s tests/resources/alices_adventures_in_wonderland.txt || wget https://www.gutenberg.org/files/11/11-0.txt -O tests/resources/alices_adventures_in_wonderland.txt
