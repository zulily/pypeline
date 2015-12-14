********
pypeline
********

Overview
========

**pypeline** provides a cli to automate management of SCM and CI components that compose a pipeline.


Example Usage
=============

Create a new gitlab project, configure the webhook, create a jenkins build project
----------------------------------------------------------------------------------

.. code-block:: bash

    $ pypeline project create --project-name=hello_world --scm-namespace=infrastructure --description="hello world pypeline project" --build-project-name=hello_world


Update an existing gitlab project to setup the jenkins webhook
--------------------------------------------------------------

.. code-block:: bash

    $ pypeline gitlab webhook --project-name=hello_world --namespace=infrastructure

Create a jenkins build project, the gitlab project already exists
-----------------------------------------------------------------

.. code-block:: bash

    $ pypeline jenkins create --build-project-name=hello_world --scm-namespace=infrastructure

List all jenkins build projects
-------------------------------

.. code-block:: bash

    $ pypeline jenkins list_projects

View a JSON representation of a Jenkins project's metadata
----------------------------------------------------------

.. code-block:: bash

    $ pypeline jenkins view --build-project hello_world

List all GitLab projects for which the authenticated user has access
--------------------------------------------------------------------

.. code-block:: bash

    $ pypeline gitlab list_projects --namespace=all

View a JSON representation of all branches for a project
--------------------------------------------------------

.. code-block:: bash

    $ pypeline gitlab list_branches --namespace=infrastructure --project-name=hello_world

View a JSON representation of all webhooks for a project
--------------------------------------------------------

.. code-block:: bash

    $ pypeline gitlab list_webhooks --namespace=infrastructure --project-name=hello_world


Command-line Reference
======================

.. argparse::
   :module: pypeline.scripts.cli
   :func: parse_arguments
   :prog: pypeline

