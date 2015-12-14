/root/.ssh/config:
  file.managed:
    - user: root
    - group: root
    - mode: 600
    - makedirs: True
    - require:
      - user: jenkins
    - contents: |
        Host *
             StrictHostKeyChecking no

/mnt/pydocs:
  file.directory:
    - user: jenkins
    - mode: 755

/mnt/pypi:
  file.directory:
    - user: jenkins
    - mode: 755

pydocs:
  glusterfs.created:
    - bricks:
        - jenkins:/glusterStor/pydocs
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

pypi:
  glusterfs.created:
    - bricks:
        - jenkins:/glusterStor/pypi
    - force: True
    - require:
      - pkg: glusterfs-server
      - pkg: glusterfs-client
      - file: /mnt/pypi
    - unless: "test -d /glusterStor/pypi/.glusterfs"

"gluster volume start pypi":
  cmd.run:
    - require:
      - glusterfs: pypi

pypi_mount:
  mount.mounted:
    - name: /mnt/pypi
    - device: localhost:pypi
    - fstype: glusterfs
    - opts: defaults,_netdev,direct-io-mode=disable
    - dump: 0
    - pass_num: 0
    - persist: True
    - require:
      - cmd: "gluster volume start pypi"

pydocs_mount:
  mount.mounted:
    - name: /mnt/pydocs
    - device: localhost:pydocs
    - fstype: glusterfs
    - opts: defaults,_netdev,direct-io-mode=disable
    - dump: 0
    - pass_num: 0
    - persist: True
    - require:
      - file: /mnt/pydocs
      - cmd: "gluster volume start pydocs"

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
            option ping-timeout 30
           option base-port 49152
        end-volume
    - require:
      - mount: pydocs_mount

"/etc/init.d/glusterfs-server restart; sleep 2; mount -a":
  cmd.run:
    - require:
      - file: /etc/glusterfs/glusterd.vol

/var/lib/glusterd/geo-replication/secret.pem:
  file.managed:
    - user: root
    - password: root
    - mode: 600
    - contents: |
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEAp61AcvMaWYIUVeDLMZbrZKbF94rVi27eohTTw0uRY1ZC0PyZ
        GZlbBSerB0d7LYZJJWxkpo9xh5JzDDioGUvjMZNjG1RFgNGODS32QoTttldoRPVN
        /NZMMt4lYIrjey3+3w3wtt9Wv04OxNyED8PAsS2Uhr8gWTSfU0sDwcAJPxVXMfd8
        U9ivvJ8o6RjAzC0XebxrIhsDffonxSbswri6B4LJC8tmvCNWeW2Jma/llagphiTv
        0A+eRvTtIOCmcwD6N3m3rLApKT94aSjsXM1Ka3X4fo0SSmxM2KajPM4sOHhmHtQL
        jFZKccjq7BR0oUqfbVS3GXA/g4FsD0RmoluZLQIDAQABAoIBAHo9gjjLJjCO9ohN
        I5V5cw6jzrtSya+nGkOLb352/v0ui/OT04GoHYU6kCL0Z8aemYDg7tfGx3uQtrL4
        MwSOIImp65ym6SyqmSbelSOViT9fpbJwK3TiPhbvgMxLNOA+fgrbPNv1ImbBX18B
        bH2Ztkb09czuVYTzKhwtGgYMHDGSDRforCM0BLEyqxZ5f6Tz7yOMpS4s9zV6tpe4
        bF3vK0dg8RE0mtr+cIupax5sZf7vwnbw4kO1aGfVW9QJ9j1Jd7/zU9BOVzvOqoz+
        aOmCJucXfapTpsQcy5yX2omfx0maSVYhy21cgY785UUa68fbG93763JmcPbuhc5N
        /vkiG7kCgYEA1LZ8DQUPZBmK3JSBrMWEUdWdUl0JmFJ5JafvPvoKDlKZ5E0FQK5Y
        4HtsC7WPqqZ5RyPToI8GqTwGxCDyZIhAYtuqIIhTC+x9OmMOwRQ8Hzn/Xl/a51gi
        +OVMw9Erlhdnm4uH0woRtg4hGvSRxPmU3ga0Hp2Boq+d+XkmGh9R1MMCgYEAycyP
        +kFLMrnazdc1Birh45iBmK9d7NK96IABRacDr9GbS4CZp4/IUfP3BJAUwvg9Wrv5
        G8qiFK5apHF1pRQLI3R8DwQIM4a7wc2Z4raua/zStDcDxtYw2oHATZjH5/uoUxDV
        EcC2MurLoqXczg2KooWF+sWK3o2+JrNJ+2qGO08CgYEAp7iXycBSqXAGcPTb5rn7
        IneXy6i2dxeYlJt85qBLK43v7/bXDHAsfhxzTixD8p+/Atv58yCzdN9yylTcK27P
        reNcmrhDGyTGfTI8IPvuiAS4GdblCQMS2EQdKk2U24zq0dfMKhhHbNBpRBLRmYnd
        2s9YWMeCvx9QJbRj2bcWU/cCgYByfhRmGSuQETCaPvK/mA7ncXx942l31y2WPyH5
        ocOOum7QjJshHYu7K57HwPN2lx9AXov8f6Ar+axFxnXH/jI/oHROlKwOh+/5Ciy4
        G4ukiyIEy33iD15SavFvVTJ+ZSLgVhl9ZAg7pUl5837ujXJNuVIFsJSUpnjvPiPI
        eGzGMwKBgQDJLVwD6FoaBbhuHrpJavpOlGvtl2aNyf0gkAVhCmrzShOG+n1XMkxy
        ryEcE9dZwd5IMXti52jvDpFIXW6a96P1mEAviYf/01R1gKSIfNIpqA8jD3YIgzBL
        o9+PBsQ50QTR7LP3t4z77g5OWGeB1RnpXKCUqzaqbh0pCAAaRRRamg==
        -----END RSA PRIVATE KEY-----

/root/.ssh/id_rsa:
  file.managed:
    - user: root
    - password: root
    - mode: 600
    - makedirs: True
    - contents: |
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEAp61AcvMaWYIUVeDLMZbrZKbF94rVi27eohTTw0uRY1ZC0PyZ
        GZlbBSerB0d7LYZJJWxkpo9xh5JzDDioGUvjMZNjG1RFgNGODS32QoTttldoRPVN
        /NZMMt4lYIrjey3+3w3wtt9Wv04OxNyED8PAsS2Uhr8gWTSfU0sDwcAJPxVXMfd8
        U9ivvJ8o6RjAzC0XebxrIhsDffonxSbswri6B4LJC8tmvCNWeW2Jma/llagphiTv
        0A+eRvTtIOCmcwD6N3m3rLApKT94aSjsXM1Ka3X4fo0SSmxM2KajPM4sOHhmHtQL
        jFZKccjq7BR0oUqfbVS3GXA/g4FsD0RmoluZLQIDAQABAoIBAHo9gjjLJjCO9ohN
        I5V5cw6jzrtSya+nGkOLb352/v0ui/OT04GoHYU6kCL0Z8aemYDg7tfGx3uQtrL4
        MwSOIImp65ym6SyqmSbelSOViT9fpbJwK3TiPhbvgMxLNOA+fgrbPNv1ImbBX18B
        bH2Ztkb09czuVYTzKhwtGgYMHDGSDRforCM0BLEyqxZ5f6Tz7yOMpS4s9zV6tpe4
        bF3vK0dg8RE0mtr+cIupax5sZf7vwnbw4kO1aGfVW9QJ9j1Jd7/zU9BOVzvOqoz+
        aOmCJucXfapTpsQcy5yX2omfx0maSVYhy21cgY785UUa68fbG93763JmcPbuhc5N
        /vkiG7kCgYEA1LZ8DQUPZBmK3JSBrMWEUdWdUl0JmFJ5JafvPvoKDlKZ5E0FQK5Y
        4HtsC7WPqqZ5RyPToI8GqTwGxCDyZIhAYtuqIIhTC+x9OmMOwRQ8Hzn/Xl/a51gi
        +OVMw9Erlhdnm4uH0woRtg4hGvSRxPmU3ga0Hp2Boq+d+XkmGh9R1MMCgYEAycyP
        +kFLMrnazdc1Birh45iBmK9d7NK96IABRacDr9GbS4CZp4/IUfP3BJAUwvg9Wrv5
        G8qiFK5apHF1pRQLI3R8DwQIM4a7wc2Z4raua/zStDcDxtYw2oHATZjH5/uoUxDV
        EcC2MurLoqXczg2KooWF+sWK3o2+JrNJ+2qGO08CgYEAp7iXycBSqXAGcPTb5rn7
        IneXy6i2dxeYlJt85qBLK43v7/bXDHAsfhxzTixD8p+/Atv58yCzdN9yylTcK27P
        reNcmrhDGyTGfTI8IPvuiAS4GdblCQMS2EQdKk2U24zq0dfMKhhHbNBpRBLRmYnd
        2s9YWMeCvx9QJbRj2bcWU/cCgYByfhRmGSuQETCaPvK/mA7ncXx942l31y2WPyH5
        ocOOum7QjJshHYu7K57HwPN2lx9AXov8f6Ar+axFxnXH/jI/oHROlKwOh+/5Ciy4
        G4ukiyIEy33iD15SavFvVTJ+ZSLgVhl9ZAg7pUl5837ujXJNuVIFsJSUpnjvPiPI
        eGzGMwKBgQDJLVwD6FoaBbhuHrpJavpOlGvtl2aNyf0gkAVhCmrzShOG+n1XMkxy
        ryEcE9dZwd5IMXti52jvDpFIXW6a96P1mEAviYf/01R1gKSIfNIpqA8jD3YIgzBL
        o9+PBsQ50QTR7LP3t4z77g5OWGeB1RnpXKCUqzaqbh0pCAAaRRRamg==
        -----END RSA PRIVATE KEY-----

# Some /bin/true to work with older versions of gluster
"gluster system:: execute gsec_create || /bin/true":
  cmd.run:
    - require:
      - mount: pydocs_mount
      - mount: pypi_mount
    - unless: "test -f /var/lib/glusterd/geo-replication/common_secret.pem.pub"

"sleep 3; gluster volume geo-replication pypi ssh://georep@pypi::pypi create push-pem 2>/dev/null || /bin/true; gluster volume geo-replication pypi ssh://georep@pypi::pypi start":
  cmd.run:
    - require:
      - cmd: "gluster system:: execute gsec_create || /bin/true"

"sleep 3; gluster volume geo-replication pydocs ssh://georep@pydocs::pydocs create push-pem 2>/dev/null || /bin/true; gluster volume geo-replication pydocs ssh://georep@pydocs::pydocs start":
  cmd.run:
    - require:
      - cmd: "gluster system:: execute gsec_create || /bin/true"

