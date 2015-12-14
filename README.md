pypeline
========
**pypeline** is a python package that simplifies management of components that may be used in a python package CI/CD pipeline. Examples include setup of jenkins build projects and creation of GitLab projects/repositories.

It currently only supports Jenkins and GitLab for the CI and SCM frameworks respectively, but it is designed to be pluggable.

Documentation
--------------
For the full API reference and CLI usage with examples, please see the [full project documentation](http://zulily.github.io/pypeline/).

The [tutorial](http://zulily.github.io/pypeline/tutorial.html) contains detailed instructions on Jenkins and glusterfs setup, and example SaltStack states
are provided to assist in the process.

Prerequisites
--------------

*To get up and running, the following must be installed:*

+ python 2.7.x
+ python-pip

Installation
------------

+ Create a virtual environment and activate
+ Clone this git repository
+ pip install .

*Optionally for sphinx document generation, pip install the following*

+ sphinx
+ pygments
+ sphinx_rtd_theme
+ sphinx-argparse

*It is important to set a few environment variables*

+ **PYPELINE_GITLAB_HOST** - The fqdn of the GitLab host.
+ **PYPELINE_GITLAB_WEBHOOK** - The GitLab webhook url, for example: https://jenkins.example.com/gitlab/build_now
+ **PYPELINE_JENKINS_HOST** - The fqdn of the jenkins host.  Requires https and it is possible to append :<port>
+ **PYPELINE_EMAIL** - The e-mail address for Jenkins build notifications.
+ **PYPELINE_SSL_NO_VERIFY** - Provides an encrypted communication channel, but does not verify the server's identity (both Jenkins and GitLab). Use with caution. Accepts True or False.


Example CLI Usage
-----------------

**Create a hello_world project in the infrastructure GitLab namespace, as well as a Jenkins build project.
Assumes Jenkins and GitLab are properly configured, see the [tutorial](http://zulily.github.io/pypeline/tutorial.html) for
guidance**

```bash
pypeline project create --project-name=hello_world --scm-namespace=infrastructure --description="hello world pypeline project" --build-project-name=hello_world
```

ToDo and Ideas for the Future
-----------------------------
+ Support for additional SCM systems and CI frameworks, with an argparse refactor -- plugins will contain
  args
+ Develop and bundle additional SCons builder scripts
+ Bundle a simple web-app that indexes the documentation and versions
+ Enhance automation regarding the bringing up of pipeline components, by leveraging SaltStack further
+ Bring up a functional local pypi service with additional SaltStack states

License
-------
Apache License, version 2.0.  Please see LICENSE
