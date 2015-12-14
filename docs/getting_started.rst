***************
Getting Started
***************

Installation
============

pip (aka the easy way)
----------------------
Assuming ~/pip/pip.conf points to a pypi repository containing
pypeline...


.. code-block:: bash

    pip install pypeline

.. note:: This is typically performed within a python virtual environment.

Manual
------

Activate a virtual environment and perform the installation from the top-level
pypeline package container directory.

.. code-block:: bash

   pip install .

And for *optional* document generation with sphinx, install the following python packages as well:

.. code-block:: bash

    pip install sphinx
    pip install pygments
    pip install sphinx_rtd_theme
    pip install sphinx-argparse


Basic Usage
===========

**Create a hello_world project**::


    #! /usr/bin/env python

    import sys

    from pypeline.scm.gl import GitLab
    from pypeline.ci.jenkins_ci import JenkinsCI

    def main():
        """Create a hello_world project (GitLab and Jenkins),
        in the infrstructure namespace.
        """
        gitlab = GitLab(gitlab_host='gitlab.example.com', user='bhodges',
                        password='my_secret_password') # Token auth also possible
        jenkins = JenkinsCI(jenkins_host='jenkins.example.com', user='bhodges',
                            password='my_secret_password') # Token auth also possible
        jenkins.create_project(project_name='hello_world', scm_project_name='hello_world',
                               namespace='infrastructure', scm_user='git',
                               scm_host='gitlab.example.com', scons_script='default_packager',
                               email='pypeline@example.com')
        gitlab.create_project(project_name='hello_world', namespace='infrastructure',
                              url='https://jenkins.example.com/gitlab/build_now',
                              description='My hello_world project...')

    if __name__ == '__main__':
        sys.exit(main())

*For additional usage examples, reviewing the* :doc:`pypeline` *cli* source is recommended
