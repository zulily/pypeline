jenkins:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - pkg: jenkins
    - watch:
      - file: /etc/default/jenkins

# It would be nice to improve this and put settings in pillar.
# etc_default_jenkins is just a static file for now, which
# must be edited if the listening ip or port must be changed...
/etc/default/jenkins:
  file.managed:
    - source: salt://jenkins/files/etc_default_jenkins
    - mode: 640
    - user: root
    - group: root
    - template: jinja
    - require:
      - pkg: jenkins
