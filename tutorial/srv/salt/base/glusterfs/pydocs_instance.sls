openssh-server:
  pkg.installed: []
  service.running:
    - name: ssh
    - require:
      - pkg: openssh-server

georep:
  user.present:
    - system: True

? AAAAB3NzaC1yc2EAAAADAQABAAABAQCnrUBy8xpZghRV4MsxlutkpsX3itWLbt6iFNPDS5FjVkLQ/JkZmVsFJ6sHR3sthkklbGSmj3GHknMMOKgZS+Mxk2MbVEWA0Y4NLfZChO22V2hE9U381kwy3iVgiuN7Lf7fDfC231a/Tg7E3IQPw8CxLZSGvyBZNJ9TSwPBwAk/FVcx93xT2K+8nyjpGMDMLRd5vGsiGwN9+ifFJuzCuLoHgskLy2a8I1Z5bYmZr+WVqCmGJO/QD55G9O0g4KZzAPo3ebessCkpP3hpKOxczUprdfh+jRJKbEzYpqM8ziw4eGYe1AuMVkpxyOrsFHShSp9tVLcZcD+DgWwPRGaiW5kt georep@example.com
:
  ssh_auth.present:
    - user: georep
    - enc: ssh-rsa
    - require:
      - user: georep

/mnt/pydocs:
  file.directory:
    - user: georep
    - mode: 755
    - require:
      - user: georep

pydocs:
  glusterfs.created:
    - bricks:
        - pydocs:/glusterStor/pydocs
    - force: True
    - require:
      - pkg: glusterfs-server
      - pkg: glusterfs-client
      - file: /mnt/pydocs
    - unless: "test -d /glusterStor/pydocs/.glusterfs"

"gluster volume start pydocs":
  cmd.run:
    - require:
      - glusterfs: pydocs

pydocs_mount:
  mount.mounted:
    - name: /mnt/pydocs
    - device: localhost:pydocs
    - fstype: glusterfs
    - opts: defaults,_netdev,direct-io-mode=disable,ro
    - dump: 0
    - pass_num: 0
    - persist: True
    - require:
      - file: /mnt/pydocs
      - cmd: "gluster volume start pydocs"

/var/mountbroker-root:
  file.directory:
    - user: root
    - group: root
    - mode: 711

/etc/glusterfs/glusterd.vol:
  file.managed:
    - user: root
    - group: root
    - mode: 644
    - contents: |
        volume management
            type mgmt/glusterd
            option working-directory /var/lib/glusterd
            option transport-type socket,rdma
            option transport.socket.keepalive-time 10
            option transport.socket.keepalive-interval 2
            option transport.socket.read-fail-log off
            option mountbroker-root /var/mountbroker-root
            option geo-replication-log-group georep
            option mountbroker-geo-replication.georep pydocs
            option base-port 49152
        end-volume
    - require:
        - mount: pydocs_mount
        - file: /var/mountbroker-root

"umount /mnt/pydocs; /etc/init.d/glusterfs-server restart; mount /mnt/pydocs":
  cmd.run:
    - require:
      - file: /etc/glusterfs/glusterd.vol
