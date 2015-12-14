jenkins_repo:
    pkgrepo.managed:
        - humanname: jenkins
        - name: deb http://pkg.jenkins-ci.org/debian binary/
        - file: /etc/apt/sources.list.d/jenkins.list
        - key_url: https://jenkins-ci.org/debian/jenkins-ci.org.key
