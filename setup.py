#! /usr/bin/env python
#
# Copyright (C) 2015 zulily, llc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pypeline"""

from setuptools import setup, find_packages

execfile('pypeline/version.py')

setup(name='pypeline',
      version=__version__,
      description="""Configure CI pipeline components for python package development""",
      author='zulily, llc',
      author_email='opensource@zulily.com',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pypeline = pypeline.scripts.cli:main'
          ]
      },
      package_data={'pypeline': ['templates/*']},
      install_requires=[
          'jinja2',
          'python-jenkins',
          'pyapi-gitlab',
          'pyyaml',
          'requests',
      ])
