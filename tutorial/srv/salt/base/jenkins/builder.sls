# Add custom builders here, an SConstruct file and optionally a different bootstrap.sh
/opt/scons/default_builder/SConstruct:
  file.managed:
    - source: salt://jenkins/files/default_builder_SConstruct
    - user: root
    - group: root
    - mode: 755
    - makedirs: True


/opt/scons/default_builder/bootstrap.sh:
  file.managed:
    - source: salt://jenkins/files/bootstrap.sh
    - user: root
    - group: root
    - mode: 755
    - makedirs: True
