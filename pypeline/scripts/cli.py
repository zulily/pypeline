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
"""pypeline - setup CI/CD pipepline components"""


#
#  ToDo: there are a large number of arguments and some amount of redundancy that would be
#  nice to clean up, however, the conflict resolution when having multiple argparse parents
#  with the same grand parent does not appear to function properly.
#

from __future__ import print_function

import argparse
import getpass
import json
import logging
import os
import sys

from pypeline import __version__ as pypeline_version
from pypeline.scm.gl import GitLab
from pypeline.ci.jenkins_ci import JenkinsCI


def main():
    """Do some stuff"""
    # Parse all command line argument
    args = parse_arguments().parse_args()

    # Setup logging
    configure_logging(args)
    logging.debug(args)

    # Prompt for password if token unspecified
    password = None
    if ('scm_token' in args and 'ci_token' in args and \
       (not args.scm_token or not args.ci_token)) or \
       (('scm_token' in args and not args.scm_token) and ('ci_token' not in args)) or \
       (('ci_token' in args and not args.ci_token) and ('scm_token' not in args)):
        password = getpass.getpass(prompt='Password ({0}): '.format(args.user))

    if args.subcommand == 'project':
        gitlab = GitLab(gitlab_host=args.scm_host, user=args.user,
                        password=password, token=args.scm_token,
                        ssl_no_verify=args.ssl_no_verify)
        jenkins = JenkinsCI(jenkins_host=args.ci_host, user=args.user,
                            password=password, token=args.ci_token,
                            ssl_no_verify=args.ssl_no_verify)
        if args.subcommand_action == 'create':
            scm_project_name = args.scm_project_name if hasattr(args, 'scm_project_name') and \
                               args.scm_project_name \
                               else args.ci_project_name
            jenkins.create_project(args.ci_project_name, scm_project_name, args.scm_namespace,
                                   args.scm_user, args.scm_host, args.scons_script, args.email)
            gitlab.create_project(args.scm_project_name, namespace=args.scm_namespace,
                                  url=args.scm_webhook_url, description=args.scm_description)
    elif args.subcommand == 'gitlab':
        gitlab = GitLab(gitlab_host=args.scm_host, user=args.user,
                        password=password, token=args.scm_token,
                        ssl_no_verify=args.ssl_no_verify)
        if args.subcommand_action == 'list_projects':
            projects = sorted(gitlab.list_projects(args.scm_namespace))
            if projects:
                print('\n{0} projects visible to me (namespace == {1}):\n'.\
                      format(len(projects), args.scm_namespace))
                for project in sorted(projects):
                    print(project)
                print()
            else:
                print('\n0 projects (namespace == {0})\n'.format(args.scm_namespace))
        elif args.subcommand_action == 'create':
            gitlab.create_project(args.scm_project_name, namespace=args.scm_namespace,
                                  url=args.scm_webhook_url, description=args.scm_description)
        elif args.subcommand_action == 'webhook':
            gitlab.set_webhook(project_name=args.scm_project_name, namespace=args.scm_namespace,
                               url=args.scm_webhook_url)
        elif args.subcommand_action == 'list_branches':
            print(json.dumps(gitlab.list_branches(project_name=args.scm_project_name,
                                                  namespace=args.scm_namespace), indent=2))
        elif args.subcommand_action == 'list_webhooks':
            print(json.dumps(gitlab.list_webhooks(project_name=args.scm_project_name,
                                                  namespace=args.scm_namespace), indent=2))
        elif args.subcommand_action == 'list_tags':
            print(json.dumps(gitlab.list_tags(project_name=args.scm_project_name,
                                              namespace=args.scm_namespace), indent=2))
        elif args.subcommand_action == 'view':
            print(json.dumps(gitlab.get_project(project_name=args.scm_project_name,
                                                namespace=args.scm_namespace), indent=2))

    elif args.subcommand == 'jenkins':
        jenkins = JenkinsCI(jenkins_host=args.ci_host, user=args.user,
                            password=password, token=args.ci_token,
                            ssl_no_verify=args.ssl_no_verify)
        if args.subcommand_action == 'list_projects':
            projects = jenkins.list_projects()
            if projects:
                print('\n{0} projects:\n'.format(len(projects)))
                for project in sorted(projects, key=lambda x: x['name']):
                    print('{0} ({1}): {2}'.\
                          format(project['name'], project['color'], project['url']))
                print()
            else:
                print('\n0 projects found.\n')
        elif args.subcommand_action == 'create':
            scm_project_name = args.scm_project_name if hasattr(args, 'scm_project_name') and \
                               args.scm_project_name \
                               else args.ci_project_name
            jenkins.create_project(args.ci_project_name, scm_project_name, args.scm_namespace,
                                   args.scm_user, args.scm_host, args.scons_script, args.email)
        elif args.subcommand_action == 'enable':
            jenkins.enable_project(args.ci_project_name)
        elif args.subcommand_action == 'disable':
            jenkins.disable_project(args.ci_project_name)
        elif args.subcommand_action == 'delete':
            jenkins.delete_project(args.ci_project_name)
        elif args.subcommand_action == 'view':
            print(json.dumps(jenkins.view_project(args.ci_project_name), indent=2))


def configure_logging(args):
    """Logging to console
    """
    log_format = logging.Formatter('%(levelname)s:%(name)s:line %(lineno)s:%(message)s')
    log_level = logging.INFO if args.verbose else logging.WARN
    log_level = logging.DEBUG if args.debug else log_level
    console = logging.StreamHandler()
    console.setFormatter(log_format)
    console.setLevel(log_level)
    root_logger = logging.getLogger()
    if len(root_logger.handlers) == 0:
        root_logger.addHandler(console)
    root_logger.setLevel(log_level)
    root_logger.handlers[0].setFormatter(log_format)
    logger = logging.getLogger(__name__)

    return logger


def parse_arguments():
    """Collect command-line arguments.  Let the caller run parse_args(), as
    sphinx-argparse requires a function that returns an instance of
    argparse.ArgumentParser
    """
    # Pull a few settings from the environment, should they exist
    gitlab_host = os.environ['PYPELINE_GITLAB_HOST'] if 'PYPELINE_GITLAB_HOST' in os.environ \
                  else 'gitlab'
    gitlab_webhook_url = os.environ['PYPELINE_GITLAB_WEBHOOK_URL'] \
                         if 'PYPELINE_GITLAB_WEBHOOK_URL' in os.environ \
                         else 'https://jenkins/gitlab/build_now'
    jenkins_host = os.environ['PYPELINE_JENKINS_HOST'] if 'PYPELINE_JENKINS_HOST' in os.environ \
                   else 'jenkins'
    email = os.environ['PYPELINE_EMAIL'] if 'PYPELINE_EMAIL' in os.environ \
            else '{0}@localhost'.format(getpass.getuser())
    ssl_no_verify = bool(os.environ['PYPELINE_SSL_NO_VERIFY'].lower().capitalize()) \
                    if 'PYPELINE_SSL_NO_VERIFY' in os.environ else False

    parser = argparse.ArgumentParser(prog='pypeline',
                                     description='A script for configuring CI pipeline components')
    parser.add_argument('-V', '--version', action='version',
                        version='pypeline v' + pypeline_version,
                        help="Print the version number and exit")
    subparsers = parser.add_subparsers(dest='subcommand', help='Sub-command help')
    parser_common = subparsers.add_parser('common', add_help=False)
    parser_common.add_argument('--user', '-u', action='store',
                               dest='user', help='The AD user to connect as, to various ' + \
                               'services, do not include the domain portion. Defaults to ' + \
                               '{0}'.format(getpass.getuser()),
                               default='{0}'.format(getpass.getuser()))
    parser_common.add_argument('--ssl-no-verify', '-s', action='store_true',
                               dest='ssl_no_verify', help="Don't verify the authenticity " + \
                               "of the server's certificate, defaults to " + \
                               "{0} and may be overridden with ".format(ssl_no_verify) + \
                               "PYPELINE_SSL_NO_VERIFY", default=ssl_no_verify)
    parser_common.add_argument('--verbose', '-v', action='store_true',
                               dest='verbose', help='Turn on verbose output', default=False)
    parser_common.add_argument('--debug', '-d', action='store_true',
                               dest='debug', default=False,
                               help="Print out debugging information, very chatty")
    parser_gitlab = subparsers.add_parser('gitlab',
                                          help='Configure gitlab projects')
    gitlab_subparsers = parser_gitlab.add_subparsers()
    parser_gitlab_common = gitlab_subparsers.add_parser('gitlab_common',
                                                        parents=[parser_common],
                                                        add_help=False)
    parser_gitlab_common.add_argument('--gl-token', '-t', action='store', metavar='TOKEN',
                                      dest='scm_token', help='The GitLab API token to use.  ' + \
                                      'If unspecified, user/password credentials will be used ')
    parser_gitlab_common.add_argument('--gitlab-host', '-H', action='store',
                                      default='{0}'.format(gitlab_host),
                                      dest='scm_host', metavar='GITLAB_HOST',
                                      help='The GitLab host, may be overriden with ' + \
                                      'PYPELINE_GITLAB_HOST and defaults to: ' + \
                                      '{0}'.format(gitlab_host))
    parser_gitlab_common.add_argument('--namespace', '-N', action='store', required=True,
                                      dest='scm_namespace', metavar='NAMESPACE',
                                      help='The GitLab namespace if applicable.  ' + \
                                      'For some subcommands, "all" may be ' + \
                                      'specified, such as for list_projects')
    parser_gitlab_create = gitlab_subparsers.add_parser('create',
                                                        parents=[parser_gitlab_common],
                                                        conflict_handler='resolve',
                                                        help='Create a gitlab project')
    parser_gitlab_create.set_defaults(subcommand_action='create')
    parser_gitlab_create.add_argument('--project-name', '-P', action='store', required=True,
                                      dest='scm_project_name', metavar='PROJECT_NAME',
                                      help='The GitLab project name.  ' + \
                                      'Do not include the namespace in the project name')
    parser_gitlab_create.add_argument('--description', '-D', action='store', required=True,
                                      dest='scm_description', metavar='DESCRIPTION',
                                      default='',
                                      help='The GitLab project description.  ')
    parser_gitlab_create.add_argument('--url', '-u', action='store',
                                      dest='scm_webhook_url', metavar='URL',
                                      default=gitlab_webhook_url,
                                      help='The webhook url.  Defaults to: ' + \
                                      '{0}'.format(gitlab_webhook_url))
    parser_gitlab_list_projects = gitlab_subparsers.add_parser('list_projects',
                                                               parents=[parser_gitlab_common],
                                                               conflict_handler='resolve',
                                                               help='List GitLab projects')
    parser_gitlab_list_projects.set_defaults(subcommand_action='list_projects')
    parser_gitlab_webhook = gitlab_subparsers.add_parser('webhook', parents=[parser_gitlab_common],
                                                         conflict_handler='resolve',
                                                         help='Update a GitLab project to ' + \
                                                         'set the webhook')
    parser_gitlab_webhook.set_defaults(subcommand_action='webhook')
    parser_gitlab_webhook.add_argument('--project-name', '-P', action='store', required=True,
                                       dest='scm_project_name', metavar='PROJECT_NAME',
                                       help='The GitLab project name.  ' + \
                                       'Do not include the namespace in the project name')
    parser_gitlab_webhook.add_argument('--url', '-u', action='store',
                                       dest='scm_webhook_url', metavar='URL',
                                       default=gitlab_webhook_url,
                                       help='The webhook url.  Defaults to: ' + \
                                       '{0}'.format(gitlab_webhook_url))
    parser_gitlab_list_branches = gitlab_subparsers.add_parser('list_branches',
                                                               parents=[parser_gitlab_common],
                                                               conflict_handler='resolve',
                                                               help='List branches ' + \
                                                               'for a GitLab project')
    parser_gitlab_list_branches.set_defaults(subcommand_action='list_branches')
    parser_gitlab_list_branches.add_argument('--project-name', '-P', action='store', required=True,
                                             dest='scm_project_name', metavar='PROJECT_NAME',
                                             help='The GitLab project name.  ' + \
                                             'Do not include the namespace in the project name')
    parser_gitlab_list_webhooks = gitlab_subparsers.add_parser('list_webhooks',
                                                               parents=[parser_gitlab_common],
                                                               conflict_handler='resolve',
                                                               help='List webhooks ' + \
                                                               'for a GitLab project')
    parser_gitlab_list_webhooks.set_defaults(subcommand_action='list_webhooks')
    parser_gitlab_list_webhooks.add_argument('--project-name', '-P', action='store', required=True,
                                             dest='scm_project_name', metavar='PROJECT_NAME',
                                             help='The GitLab project name.  ' + \
                                             'Do not include the namespace in the project name')
    parser_gitlab_view = gitlab_subparsers.add_parser('view', parents=[parser_gitlab_common],
                                                      conflict_handler='resolve',
                                                      help='View details for a ' + \
                                                      'GitLab project')
    parser_gitlab_view.set_defaults(subcommand_action='view')
    parser_gitlab_view.add_argument('--project-name', '-P', action='store', required=True,
                                    dest='scm_project_name', metavar='PROJECT_NAME',
                                    help='The GitLab project name.  ' + \
                                    'Do not include the namespace in the project name')
    parser_gitlab_list_tags = gitlab_subparsers.add_parser('list_tags',
                                                           parents=[parser_gitlab_common],
                                                           conflict_handler='resolve',
                                                           help='List tags for a ' + \
                                                           'GitLab project')
    parser_gitlab_list_tags.set_defaults(subcommand_action='list_tags')
    parser_gitlab_list_tags.add_argument('--project-name', '-P', action='store', required=True,
                                         dest='scm_project_name', metavar='PROJECT_NAME',
                                         help='The GitLab project name.  ' + \
                                         'Do not include the namespace in the project name')
    parser_jenkins = subparsers.add_parser('jenkins',
                                           help='Configure Jenkins projects')
    jenkins_subparsers = parser_jenkins.add_subparsers()
    parser_jenkins_common = jenkins_subparsers.add_parser('jenkins_common',
                                                          parents=[parser_common],
                                                          add_help=False,
                                                          conflict_handler='resolve')
    parser_jenkins_common.add_argument('--ci-token', '-T', action='store', dest='ci_token',
                                       help='The CI API token to use. ' + \
                                       'If unspecified, user/password credentials will be ' + \
                                       'used. May not be supported by all CI frameworks')
    parser_jenkins_common.add_argument('--jenkins-host', '-J', action='store',
                                       default='{0}'.format(jenkins_host),
                                       dest='ci_host', help='The Jenkins CI host, defaults to: ' + \
                                       '{0}'.format(jenkins_host))
    parser_jenkins_common_project = jenkins_subparsers.add_parser('jenkins_common_project',
                                                                  parents=[parser_jenkins_common],
                                                                  add_help=False,
                                                                  conflict_handler='resolve')
    parser_jenkins_common_project.add_argument('--build-project-name', '-B', action='store',
                                               required=True, dest='ci_project_name',
                                               metavar='BUILD_PROJECT_NAME',
                                               help='The Jenkins project name.  ')
    parser_jenkins_list_projects = jenkins_subparsers.add_parser('list_projects',
                                                                 parents=[parser_jenkins_common],
                                                                 conflict_handler='resolve',
                                                                 help='List Jenkins projects')
    parser_jenkins_list_projects.set_defaults(subcommand_action='list_projects')
    parser_jenkins_create = jenkins_subparsers.add_parser('create',
                                                          parents=[parser_jenkins_common_project],
                                                          conflict_handler='resolve',
                                                          help='Create a jenkins build project')
    parser_jenkins_create.set_defaults(subcommand_action='create')
    parser_jenkins_create.add_argument('--scm-project-name', '-P', action='store',
                                       dest='scm_project_name', metavar='SCM_PROJECT_NAME',
                                       help='The SCM project name.  If unspecified, ' + \
                                       'defaults to whatever is specified with ' + \
                                       '--build-project-name')
    parser_jenkins_create.add_argument('--scm-namespace', '-N', action='store', required=True,
                                       dest='scm_namespace', metavar='NAMESPACE',
                                       help='The SCM namespace.  ')
    parser_jenkins_create.add_argument('--scm-host', '-H', action='store',
                                       default='{0}'.format(gitlab_host),
                                       dest='scm_host', metavar='SCM_HOST',
                                       help='The SCM host, defaults to: ' + \
                                       '{0}'.format(gitlab_host))
    parser_jenkins_create.add_argument('--scm-user', '-U', action='store',
                                       default='{0}'.format('git'),
                                       dest='scm_user', metavar='SCM_USER',
                                       help='The SCM user, defaults to: ' + \
                                       '{0}'.format('git'))
    parser_jenkins_create.add_argument('--scons-script', '-S', action='store',
                                       default='{0}'.format('default_builder'),
                                       dest='scons_script', metavar='SCONS_SCRIPT',
                                       help='The SCONS script, defaults to: ' + \
                                       '{0}'.format('default_builder'))
    parser_jenkins_create.add_argument('--email', '-e', action='store',
                                       default='{0}'.format(email),
                                       dest='email', metavar='EMAIL_ADDRESS',
                                       help='The notification e-mail address, defaults to: ' + \
                                       '{0}.  Overridable with PYPELINE_EMAIL'.format(email))
    parser_jenkins_enable = jenkins_subparsers.add_parser('enable',
                                                          parents=[parser_jenkins_common_project],
                                                          conflict_handler='resolve',
                                                          help='Enable a jenkins build project')
    parser_jenkins_enable.set_defaults(subcommand_action='enable')
    parser_jenkins_disable = jenkins_subparsers.add_parser('disable',
                                                           parents=[parser_jenkins_common_project],
                                                           conflict_handler='resolve',
                                                           help='Disable a jenkins build project')
    parser_jenkins_disable.set_defaults(subcommand_action='disable')
    parser_jenkins_delete = jenkins_subparsers.add_parser('delete',
                                                          parents=[parser_jenkins_common_project],
                                                          conflict_handler='resolve',
                                                          help='Delete a jenkins build project')
    parser_jenkins_delete.set_defaults(subcommand_action='delete')
    parser_jenkins_view = jenkins_subparsers.add_parser('view',
                                                        parents=[parser_jenkins_common_project],
                                                        conflict_handler='resolve',
                                                        help='View jenkins build project ' + \
                                                        'details (json)')
    parser_jenkins_view.set_defaults(subcommand_action='view')
    parser_project = subparsers.add_parser('project',
                                           help='Configure various CI pipeline component projects')
    project_subparsers = parser_project.add_subparsers()
    parser_project_create = project_subparsers.add_parser('create',
                                                          parents=[parser_jenkins_create],
                                                          conflict_handler='resolve',
                                                          help='Create CI and SCM component ' + \
                                                          'projects')
    parser_project_create.set_defaults(subcommand_action='create')
    # The conflict resolution doesn't appear to work with two parents with the same grand parent,
    # so some unfortunate copy-and-paste here.
    parser_project_create.add_argument('--gl-token', '-t', action='store', metavar='TOKEN',
                                       dest='scm_token', help='The GitLab API token to use.  ' + \
                                       'If unspecified, user/password credentials will be used ')
    parser_project_create.add_argument('--project-name', '-P', action='store', required=True,
                                       dest='scm_project_name', metavar='PROJECT_NAME',
                                       help='The GitLab project name.  ' + \
                                       'Do not include the namespace in the project name')
    parser_project_create.add_argument('--description', '-D', action='store', required=True,
                                       dest='scm_description', metavar='DESCRIPTION',
                                       default='',
                                       help='The GitLab project description.  ')
    parser_project_create.add_argument('--url', '-u', action='store',
                                       dest='scm_webhook_url', metavar='URL',
                                       default=gitlab_webhook_url,
                                       help='The webhook url.  Defaults to: ' + \
                                       '{0}'.format(gitlab_webhook_url))


    return parser


if __name__ == '__main__':
    sys.exit(main())
