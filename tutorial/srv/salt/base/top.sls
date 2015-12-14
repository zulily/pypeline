base:
  '*':
    - glusterfs

  'jenkins*':
    - jenkins
    - nginx
    - glusterfs/jenkins_instance

  'pydocs*':
    - glusterfs/pydocs_instance

  'pypi*':
    - glusterfs/pypi_instance
