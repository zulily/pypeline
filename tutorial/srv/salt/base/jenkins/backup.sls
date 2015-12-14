# Backup script not included, for an example, here is one suggestion:
# https://github.com/sue445/jenkins-backup-script/blob/master/jenkins-backup.sh

#/usr/local/bin/jenkins_backup:
#  file.managed:
#    - source: salt://jenkins/files/jenkins_backup
#    - mode: 755
#    - user: root
#    - group: root
#
#
#/backups/jenkins:
#  file.directory:
#    - user: root
#    - group: root
#    - dir_mode: 755
#    - makedirs: True
#
#
#/etc/cron.d/jenkins:
#  file.managed:
#    - user: root
#    - group: root
#    - mode: 640
#    - template: jinja
#    - source: salt://jenkins/files/jenkins_cron
#
