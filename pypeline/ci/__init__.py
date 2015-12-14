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
"""CI component management management module containing abstract base class"""

import abc

class CIBase(object):
    """The CI plugin base class

    An abstract base class for CI plugins that configure
    build projects a CI/CD pipeline.
    """
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def create_project(self, project_name, scm_project_name, namespace,
                       scm_user, scm_host, scons_script, email):
        """Create a CI build project

        :return: True or False to indicate success or failure
        :rtype: bool
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def list_projects(self):
        """List SCM projects"""
        raise NotImplementedError()

