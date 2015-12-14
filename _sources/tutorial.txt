************************************
Tutorial - Building a CI/CD Pipeline
************************************

Overview
========
This tutorial walks through the setup of a python CI/CD pipeline, with the following key
components:

+ Jenkins
+ GitLab

Once configured, ``pypeline`` may be used to automate GitLab project and Jenkins build project
creation.  While ``pypeline`` only works with GitLab and Jenkins at this time, is written in a
way that it is easily pluggable, however, some refactoring of the argument parsing will be
necessary as additional plugins are incorporated.

Goals
=====
By stepping through this tutorial, we will have a pipeline that is capable of the following:

+ Pushes to master and tagged pushes will build sphinx documentation and run integration tests
+ Tagged pushes will build and deploy documentation and release artifacts (pip-installable)

.. note:: A triggered build can do anything and the default capabilities may be extended


Assumptions
===========
+ GitLab is already up-and-running, its configuration is outside the scope of this tutorial
+ GitLab and Jenkins user accounts have a same-named direct mapping
+ A debian-based distribution is being used, although the setup should work with other distros
  with slight modifications
+ The host running test instances must has access to the running GitLab ReST API

Pre-requisites
==============
+ A test environment, built using `buoyant <https://github.com/zulily/buoyant>`_ (Docker-based), Vagrant or similar.
  The focus will be on using buoyant in this tutorial.  It is worth noting however that geo-replication will
  not function in the test environment, glusterfs bricks and docker volumes don't seem to mix.  A slower environment
  to work with (but fully functional!) is to use vagrant.  A simple 'vagrant up' in the tutorial subdirectory will
  bring up three salted minions.

Bringing Up the Pipeline
========================
The goal of this section will be to bring up three instances:

1. jenkins - the Jenkins server and source glusterfs volumes reside here
2. pydocs - documentation that is built gets geo-replicated here
3. pypi - pip-installable tarballs are geo-replicated (and served from) here

Create a Docker image using buoyant
-----------------------------------
Build a buoyant base image, using the buoyant Dockerfile.  The result will be an image
from which thick containers may be built for our test environment.  Please see the buoyant
README.md for details on building the image, but once cloned, running a command
like so is sufficient:

.. code-block:: bash

    cd ~/git/
    git clone git@github.com:zulily/buoyant.git
    cd buoyant/
    docker build -t pypeline:v15.10_2015.8.1 .

.. note:: The initial docker image build generally takes upwards of 10 minutes, spinning up containers
   is nearly instantaneous afterwards.


Bring up three Docker containers
--------------------------------
cd back to the top-level pypeline repository directory to complete these steps.

.. code-block:: bash

   docker run -d --name jenkins -h jenkins.example.com  \
   --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
   -p 127.0.0.1:5443:443 \
   -v $(pwd)/tutorial/srv:/srv \
   -v $(pwd)/tutorial/glusterStor/jenkins:/glusterStor \
   pypeline:v15.10_2015.8.1 /sbin/init

.. code-block:: bash

   docker run -d --name pydocs -h pydocs.example.com  \
   --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
   -p 127.0.0.1:6080:80 \
   -v $(pwd)/tutorial/srv:/srv \
   -v $(pwd)/tutorial/glusterStor/pydocs:/glusterStor \
   pypeline:v15.10_2015.8.1 /sbin/init

.. code-block:: bash

   docker run -d --name pypi -h pypi.example.com  \
   --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
   -p 127.0.0.1:7080:80 \
   -v $(pwd)/tutorial/srv:/srv \
   -v $(pwd)/tutorial/glusterStor/pypi:/glusterStor \
   pypeline:v15.10_2015.8.1 /sbin/init


.. note::
   Spinning up these Docker instances may switch the host system to a different tty. Alt-F[89]...

.. note::
   If rebuilding these docker instances, be sure to delete all .glusterfs and .trashcan directories first!
   docker kill pydocs jenkins pypi; docker rm pydocs jenkins pypi; sudo rm -rf tutorial/glusterStor/\*/\*


Connecting to running instances
-------------------------------
Attaching to running instances is simple and will be necessary to complete additional steps
in this tutorial.


.. code-block:: bash

    docker exec -it jenkins /bin/bash
    docker exec -it pydocs /bin/bash
    docker exec -it pypi /bin/bash

Bring up the glusterfs slaves first
-----------------------------------
.. code-block:: bash

    root@pydocs# salt-call state.highstate
    root@pypi# salt-call state.highstate

Install Jenkins, nginx and glusterfs on the jenkins instance
------------------------------------------------------------
Some basic salt states are available to install gluster and get Jenkins running with an nginx reverse-proxy.

.. code-block:: bash

    root@jenkins:/# salt-call state.highstate

.. note::
   The nginx configuration specifies a proxy_redirect directive.  Necessary for the test environment, but
   something to be removed most likely from a production configuration.  Also note that Jenkins will
   warn about an incorrect proxy configuration, but the environment is indeed functional.

Install the GitLab Hook Plugin
------------------------------
This is a manual step.  Now that Jenkins is up and running, connect to https://localhost:5443/pluginManager/available

.. note::
   The proxy redirect only works for localhost, port 5443, within the nginx configuration for
   this tutorial.  127.0.0.1 will not work unless the configuration is further modified!

Use the filter option to pair down to just the gitlab-hook plugin.  Select the plugin and click
the *Download now and Install after restart* button.  On the next screen select the option to
restart Jenkins automatically.

The Gitlab Hook plugin seems to have an issue with tag triggers.  This needs to be reported upstream,
but for now, a workaround is to edit /var/lib/jenkins/plugins/gitlab-hook/WEB-INF/classes/models/values/project.rb.
A simple example diff is as follows:

.. code-block:: diff

    --- project.rb.orig 2015-10-31 00:10:45.870662064 -0700
    +++ project.rb  2015-10-30 23:56:34.502059047 -0700
    @@ -150,6 +150,9 @@
         #
         def matches_branch?(details, branch = false, exactly = false)
           refspec = details.full_branch_reference
    +      if refspec.include? "tags"
    +       return true
    +      end
           branch = details.branch unless branch
           matched_refspecs = []
           matched_branch = nil

Apply the patch and restart the Jenkins service.

Configure Jenkins Authentication
--------------------------------
One option is to use the built-in Jenkins user account management, but most users will
prefer to authenticate with an Active Directory server, which is covered in this section.

It is necessary to connect to an AD service where the server identity is verifiable.
Export the organizational AD certificate in .CER format.  This is most easily
accomplished using the *mmc* windows management tool.  Once exported, the certificate must
be imported:

.. code-block:: bash

   # Place a copy of the certificate in /tmp and stop the jenkins service

   # Use keytool, which will prompt to set a password
   keytool -import -trustcacerts -alias ad1 -file /tmp/ad1_cert.crt

   # Also place a copy of the .crt file in /usr/local/share/ca-certificates (Ubuntu)
   update-ca-certificates

   # Start the jenkins service

Next through the admin UI, confiture LDAP authentication

+ Connect to https://localhost:5443/configureSecurity/
+ Select *Enable security*
+ Select *LDAP*
+ Specify the server url, for example: ldaps://ldap:636 (ldap+ssl)
+ Select the *Advanced...* button
+ Leave the root DN blank and select the *Allow blank rootDN* checkbox
+ Choose the *User search base*, for example: OU=Departments,DC=example,DC=com
+ Specify an LDAP filter (*User search filter*)to restrict group access, for example:
  (&(sAMAccountName={0})(memberOf:1.2.840.113556.1.4.1941:=CN=Infrastructure_Team,OU=Groups,OU=IT,OU=Departments,DC=example,DC=com))
+ Specify a *Group search base*, for example: OU=Departments,DC=example,DC=com
+ Leave *Group search filter* and *Group membership* unspecified
+ Specify a role account to connect to AD with (*Manager DN*), for example: CN=ldapuser,CN=Users,DC=example,DC=com
+ Specify the *Manager Password*
+ Specify the *Display Name LDAP attribute*, e.g.: **displayname**
+ Specify the *Email Address LDAP attribute*, e.g.: **mail**
+ For Authorization, "Logged-in users can do anything" is a good starting place, but more granular options
  are available, such as matrix-based.

.. note::
   If authentication is ever to fail (e.g. for all users due to a configuration change),
   it is possible to recover.  First, stop the jenkins service.  After the jenkins service has
   stopped, it is possible to edit the configuration file directly:  /var/lib/jenkins/config.xml.
   If the ldap search filter is broken, it is possible to edit the userSearch value.  It is
   also possible to simply turn off authentication to have the option of fixing the
   configuration through the administration interface, set useSecurity to false.  After making
   changes to the jenkins xml configuration file, perform a jenkins service start.
   Note that as the configuation file is xml, the use of entities may be
   required, particularly in ldap search filters (e.g. &amp).


Manage Jenkins Credentials
--------------------------
A role account must exist on the GitLab server that has clone access for all repositories
that are to be part of the pipeline.  Once this account exists in GitLab, connect to Jenkins
to add a credential: https://localhost:5443/credential-store/domain/_/newCredentials

+ For *Kind*, select SSH Username with private key
+ The *Scope* is to be Global
+ Specify the *Username* for the account residing on the GitLab Server
+ Provide the *Private Key*, such as by entering it directly
+ Specify a *Passphrase* for the private key if applicable
+ Enter a description if desired
+ Click on the *Advanced...* button and specify the *ID* as "pypeline", this is a critical step
+ Click *OK* when complete

Create a GitLab and Jenkins Build Projects!
-------------------------------------------
All of the plumbing is now in place and it's time to work with the pypeline cli.  First, create a few
environment variables to set useful defaults:

.. code-block:: bash

   export PYPELINE_GITLAB_HOST="gitlab.example.com"
   export PYPELINE_GITLAB_WEBHOOK_URL="https://my_test_instance.example.com:3443/gitlab/build_now"
   export PYPELINE_JENKINS_HOST="localhost:5443"
   export PYPELINE_EMAIL="user@example.com"
   export PYPELINE_SSL_NO_VERIFY="True"

.. note::
   Adding environment variables to an rc file and re-sourcing it is recommended.


If using buoyant/docker to step through this tutorial, the GitLab server will not be able to
trigger builds, the docker instances will be listening on port 5443 of the loopback and therefore
unreachable by remote hosts.  To test things out temporarily and assuming no firewall restrictions
are in place, an ssh tunnel may be used to allow the webhook url used by GitLab to be functional.
For example:

.. code-block:: bash

   ssh -g -L 3443:localhost:5443 -f -N user@localhost

To more easily complete an end-to-end test, a vagrant environment is necessary.

From the top-level pypeline repository directory and assuming a python virtual environment has
been activated, install pypeline and create a first repository and build project:

.. code-block:: bash

   pip install .
   # Assuming there is an infrastructure namespace in GitLab and preferably with the environment variables set:
   pypeline project create --project-name=hello_world --scm-namespace=infrastructure --description="hello world pypeline project" --build-project-name=hello_world


*Python packages must meet a few requirements:*

+ <package>.__version__ must be available, with a format of <major>.<minor>.<patch>. With nothing
  installed, python setup.py --version must return the version
+ Packages must have a setup.py
+ sphinx must be installed in the virtual environment, if documentation is to be generated (handled by default)

Jenkins Build Project Overview
------------------------------
When a Jenkins build is triggered, sphinx documentation is generated (if applicable) and
an artifact is created (if applicable).  Documentation and artifacts are automatically
deployed with the glusterfs setup.

The provided SaltStack states include a Jenkins workstation bootstrap script, as well as an
SConstruct file.  The Sconstruct file does a few things:

+ Runs unit tests, if any
+ Installs the package into a virtual environment
+ Builds sphinx documentation, if a docs/Makefile exists
+ Runs a setup.py clean
+ Creates a pip-installable tarball
+ Installs documentation to a target directory
+ Installs the pip-installable tarball to a target directory

Any failure of a step in the default SConstruct file will return a non-zero
error code to the caller.


What's Next?
------------
This tutorial covers the Jenkins and glusterfs geo-replication configuration.  It does not
currently bundle a web-app to index the sphinx documentation, nor do the salt states
bring up a local pypi server at present.  These will be the next set of components
to bring up to complete the pipeline.

Once the pipeline is fully functional, creating a .pip/pip.conf file is recommended, for example:

.. code-block:: bash

   [global]
   timeout = 30
   index-url = https://pypi.example.com/simple
   trusted-host = pypi.example.com
