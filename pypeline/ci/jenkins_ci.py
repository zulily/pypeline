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
"""Management of jenkins build projects"""

from __future__ import print_function

import logging
import os
import jenkins
import requests

from jinja2 import Environment, PackageLoader
from pypeline.ci import CIBase


class JenkinsCI(CIBase):
    """
    High-level Jenkins API abstraction layer
    """

    def __init__(self, jenkins_host='jenkins', user=None, password=None, token=None,
                 ssl_no_verify=False):
        """The JenkinsCI constructor"""
        # Setup logging, assumes a root logger already exists with handlers
        self.logger = logging.getLogger(__name__)
        self.package_dir = os.path.join('/'.join(os.path.dirname(os.path.realpath(__file__)).\
                                        split('/')[:-1]))

        if ssl_no_verify:
            requests.packages.urllib3.disable_warnings()


        if user and password:
            self.server = jenkins.Jenkins('https://{0}'.format(jenkins_host), username=user,
                                          password=password)
        elif token:
            self.server = jenkins.Jenkins('https://{0}'.format(jenkins_host), username=user,
                                          password=token)
        else:
            raise ValueError("Jenkins credentials must be provided, user/password or user/token")


    def create_project(self, project_name, scm_project_name, namespace,
                       scm_user, scm_host, scons_script, email):
        """Create a Jenkins build project with SCM tie-in

        :param str project_name: the name of the Jenkins build project
        :param str scm_project_name: the name of the scm project
        :param str namespace: the namespace in which the scm project resides
        :param str scm_user: the scm user to connect as, e.g. git
        :param str scm_host: the hostname of the scm server hosting the git repository
        :param str scons_script: the name of the SCons script to use, e.g. zupy_packager
        """
        if self.server.job_exists(project_name):
            raise JenkinsCIDuplicateProjectError('A Jenkins project with name ' + \
                '{0} already exists'.format(project_name))

        env = Environment(loader=PackageLoader('pypeline', 'templates'))
        template = env.get_template('jenkins_job_config.xml')

        rendered = template.render(scm_project_name=scm_project_name, namespace=namespace,
                                   git_user=scm_user, git_host=scm_host,
                                   scons_script=scons_script, email=email
                                  )

        self.server.create_job(project_name, rendered)


    def delete_project(self, project_name):
        """Delete a Jenkins build project

        :param str project_name: the name of the Jenkins build project
        """
        self.server.delete_job(project_name)


    def list_projects(self):
        """List all Jenkins build projects

        :return: a list of build projects
        :rtype: list
        """
        return self.server.get_jobs()


    def disable_project(self, project_name):
        """Disable a Jenkins build project

        :param str project_name: the name of the Jenkins build project
        """
        self.server.disable_job(project_name)


    def enable_project(self, project_name):
        """Enable a Jenkins build project

        :param str project_name: the name of the Jenkins build project
        """
        self.server.enable_job(project_name)


    def view_project(self, project_name):
        """Retrieve build project metadata

        :param str project_name: the name of the Jenkins build project

        :return: a dictionary containing build project metadata
        :rtype: dict
        """
        return self.server.get_job_info(project_name)



class JenkinsCIDuplicateProjectError(Exception):
    """
    An exception that indicates a project with the specified name already exists
    """
    pass
