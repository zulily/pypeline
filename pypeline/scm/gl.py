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
"""Management of gitlab projects"""

from __future__ import print_function

import logging
import gitlab
import requests

from pypeline.scm import SCMBase


class GitLab(SCMBase):
    """
    High-level GitLab API abstraction layer
    """

    def __init__(self, gitlab_host='gitlab', user=None, password=None, token=None,
                 ssl_no_verify=False):
        """The GitLab constructor"""
        # Setup logging, assumes a root logger already exists with handlers
        self.logger = logging.getLogger(__name__)

        if ssl_no_verify:
            requests.packages.urllib3.disable_warnings()

        if user and password:
            self.manager = gitlab.Gitlab(gitlab_host, verify_ssl=not ssl_no_verify)
            self.manager.login(user, password)
        elif token:
            self.manager = gitlab.Gitlab(gitlab_host, token=token, verify_ssl=not ssl_no_verify)
        else:
            raise ValueError("GitLab credentials must be provided, user/password or token")


    def create_project(self, project_name, namespace=None, url=None, description=''):
        """Create a new GitLab project

        :param str project_name: The gitlab project name
        :param str namespace: The gitlab namespace under which the new project will fall
        :param str url: The webhook URL to call that triggers a build on a CI system
        """
        namespace_id = self._get_namespace_id(namespace)

        if self.manager.getproject('{0}/{1}'.format(namespace, project_name)):
            raise GitLabDuplicateProjectError('Create project - ' + \
                                              '{0}/{1} already exists'.format(namespace,
                                                                              project_name))
        self.manager.createproject(name=project_name, namespace_id=namespace_id,
                                   description=description, issues_enabled=True,
                                   merge_requests_enabled=True, wiki_enabled=True,
                                   snippets_enabled=True, public=False,
                                   visibility_level=10)

        if url:
            self.set_webhook(project_name, namespace, url)

        return True


    def list_projects(self, namespace='all'):
        """List all projects visible to the currently authenticated user, including namespace

        :param str namespace: The gitlab namespace to filter by, defaults to all (no filter)

        :return: A list of all visible GitLab projects
        :rtype: list
        """

        if namespace == 'all':
            return [project['name_with_namespace'] for project \
                    in self.manager.getall(self.manager.getprojects)]
        else:
            return [project['name_with_namespace'] for project \
                    in self.manager.getall(self.manager.getprojects) \
                    if namespace in project['namespace']['name']]


    def set_webhook(self, project_name, namespace, url, push=True, tag_push=True, issues=False,
                    merge_requests=False):
        """Set the project's webhook

        :param str project_name: The gitlab project name
        :param str namespace: The gitlab namespace under which the project resides
        :param str url: The webhook URL to call that triggers a build on a CI system
        :param bool push: Whether or not the webhook is triggered with a push event
        :param bool tag_push: Whether or not the webhook is triggered with a tag push event
        :param bool issues: Whether or not the webhook is triggered when an issue is created
        :param bool merge_requests: Whether or not the webhook is triggered with a merge
            request is created


        """
        project_id = self.manager.getproject('{0}/{1}'.format(namespace, project_name))['id']

        for webhook in self.manager.getall(self.manager.getprojecthooks, project_id=project_id):
            if webhook['url'] == url:
                raise GitLabDuplicateWebhookError('A webhook with the specified URL ' + \
                                                  'already exists ({0})'.format(url))

        self.manager.addprojecthook(project_id, url, push=push, tag_push=tag_push,
                                    issues=issues, merge_requests=merge_requests)

    def list_branches(self, project_name, namespace):
        """List a project's branches

        :param str namespace: the namespace in which the GitLab project resides
        :param str project_name: the name of the gitlab project

        :return: a list of branches for the project
        :rtype: list

        """
        project = self.get_project(project_name, namespace)

        return self.manager.getbranches(project['id'])


    def list_webhooks(self, project_name, namespace):
        """List a project's webhooks

        :param str namespace: the namespace in which the GitLab project resides
        :param str project_name: the name of the gitlab project

        :return: a list of webhooks for the project
        :rtype: list

        """
        project = self.get_project(project_name, namespace)

        return list(self.manager.getall(self.manager.getprojecthooks, project['id']))


    def list_tags(self, project_name, namespace):
        """List a project's tags. Seems broken with the current revision of the GitLab REST API.

        :param str namespace: the namespace in which the GitLab project resides
        :param str project_name: the name of the gitlab project

        :return: a list of tags for the project
        :rtype: list

        """
        raise NotImplementedError
        #project = self.get_project(project_name, namespace)

        #return list(self.manager.getall(self.manager.getrepositorytree, project['id']))


    def get_project(self, project_name, namespace):
        """Retrieve project information

        :param str namespace: the namespace in which the GitLab project resides
        :param str project_name: the name of the gitlab project

        :return: a representation of a project
        :rtype: a dictionary

        """
        return self.manager.getproject('{0}/{1}'.format(namespace, project_name))


    def _get_namespace_id(self, namespace):
        """Retrieve a namespace, given its name.  This is ugly,
        but pyapi-gitlab doesn't yet implement namespace functions.

        :param str name: the namespace's name

        :return: a namespace id
        :rtype: int
        """
        projects = [project for project in self.manager.getall(self.manager.getprojects) \
                    if namespace in project['namespace']['name']]

        try:
            namespace_id = projects[0]['namespace']['id']
        except:
            raise GitLabNamespaceError('Unable to retrieve namespace_id for ' + \
                                       '"{0}" namespace'.format(namespace))

        return namespace_id


class GitLabNamespaceError(Exception):
    """
    An exception that represents the inability to lookup a namespace or access its metadata
    """
    pass


class GitLabDuplicateProjectError(Exception):
    """An exception indicating a project of the same already exists"""
    pass


class GitLabDuplicateWebhookError(Exception):
    """An exception indicating a project already has a webhook with the same url"""
