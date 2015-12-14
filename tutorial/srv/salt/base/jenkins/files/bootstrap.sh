#!/bin/bash

(test -d venv && source venv/bin/activate && pip install --egg scons --upgrade) || (virtualenv venv && source venv/bin/activate && pip install --egg scons)

source venv/bin/activate
pip install sphinx --upgrade
pip install sphinx-argparse --upgrade
# install pychecker or pep8?

scons package_name=`python -c 'import os; print os.environ["REPOSITORY.NAME"]'` ref=${REF} object_kind=${OBJECT_KIND} workspace=${WORKSPACE}
