ssl-cert:
  pkg.installed

nginx:
  pkg.installed: []
  service.running:
    - name: nginx
    - enable: True
    - require:
      - pkg: nginx
      - pkg: ssl-cert
    - watch:
      - file: /etc/nginx/nginx.conf
      - file: /etc/nginx/sites-available/jenkins

/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf
    - template: jinja

/etc/nginx/sites-available/default:
  file.absent

/etc/nginx/sites-enabled/default:
  file.absent

/etc/nginx/sites-available/jenkins:
  file.managed:
    - source: salt://nginx/files/jenkins
    - template: jinja
    - require:
      - file: /etc/nginx/sites-available/default

/etc/nginx/sites-enabled/jenkins:
  file.symlink:
    - target: /etc/nginx/sites-available/jenkins
    - require:
      - file: /etc/nginx/sites-available/jenkins
    - watch_in:
      - service: nginx
