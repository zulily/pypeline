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
"""SCM plugin module containing abstract base class"""

import abc

class SCMBase(object):
    """The SCM plugin base class

    An abstract base class for SCM plugins that configure
    projects and repositories that are part of a CI/CD
    pipeline.
    """
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def create_project(self, project_name, namespace, url, description):
        """Create an SCM project/repository

        :param str name: the name of the project/repository
        :param str namespace: the name of the project/repository

        :return: True or False to indicate success or failure
        :rtype: bool
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def list_projects(self, namespace):
        """List SCM projects"""
        raise NotImplementedError()


    @abc.abstractmethod
    def set_webhook(self, project_name, namespace, url, push, tag_push, issues,
                    merge_requests=False):
        """Setup the webhook"""
        raise NotImplementedError()
