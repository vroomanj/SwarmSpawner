# vroomanj/jupyterhub:latest

**This container image CANNOT be built (won't work) without first creating a `jupyterhub_config.py` in the `other-files/` directory. Make a copy of `jupyterhub_config.py.example` and modify as necessary.**

This Dockerfile and included example files builds a CentOS-based JupyterHub Docker container image using my modified version of cassinyio/SwarmSpawner as the spawner. This example proxies SSSD requests to the host system (Docker Swarm manager) for user look up and authentication (example: LDAP/Kerberos) and thus is intended to spawn system user images. It can be configured to either contain all of the necessary runtime files or rely on bind mounts (see the commented sections in the Dockerfile). As is, it expects the JupyterHub config to be bind mounted into `/etc/jupyterhub` (ro) and the server runtime directory to be bind mounted into `/srv/jupyterhub` (rw). If you have a need to preserve JupyterHub logs long-term you will want to modify the Dockerfile and bind mount the desired log directory into `/log/jupyterhub` (rw).

More details forthcoming...

On the host system (Docker Swarm manager):
```
groupadd --gid 1000 jupyter
useradd --uid 1000 --gid jupyter --groups docker --home-dir /etc/jupyterhub --create-home jupyter
```

On the host system (Docker Swarm manager):
```
ln -s /etc/pam.d/system-auth-ac /etc/pam.d/sss-proxy
```

On the host system (Docker Swarm manager):
```
[sssd]
domains = DOM, proxy
services = nss, pam
config_file_version = 2

[nss]
filter_groups = root
filter_users = root

[pam]

[domain/DOM]
enumerate = {true|false}
id_provider = ldap
chpass_provider = krb5
ldap_uri = ldap://ldap_uri.example.com/
ldap_user_search_base = dc=example,dc=com
ldap_krb5_keytab = {/path/filename.keytab}
tls_reqcert = {never|allow|try|demand}

auth_provider = krb5
krb5_server = {krb5_server.example.com}
krb5_realm = {EXAMPLE.COM}
krb5_changepw_principal = kadmin/changepw
krb5_ccachedir = {/path}
krb5_ccname_template = FILE:%d/krb5cc_%U_XXXXXX
krb5_auth_timeout = {integer (seconds)}

[domain/proxy]
id_provider = proxy
auth_provider = proxy
# The proxy provider will look into ldap for user info
proxy_lib_name = sss
# The proxy provider will authenticate against /etc/pam.d/sss-proxy
proxy_pam_target = sss-proxy
```

On the host system (Docker Swarm manager):
```
git clone https://github.com/vroomanj/SwarmSpawner.git
cd SwarmSpawner/
cp jupyterhub/other-files/jupyterhub_config.py.example jupyterhub/other-files/jupyterhub_config.py
**MODIFY*** jupyterhub/other-files/jupyterhub_config.py
docker build jupyterhub/ -t vroomanj/jupyterhub:latest
```

On the host system (Docker Swarm manager):
```
docker network create --opt encrypted --driver overlay jupyterhub
```

On all Docker Swarm nodes including the manager (if using Firewalld):
```
firewall-cmd --zone=docker --permanent --add-rich-rule="rule protocol value=esp accept"
```

On the host system (Docker Swarm manager):
```
docker service create --constraint 'node.role == manager' --name jupyterhub --network jupyterhub \
       --dns IP1.IP1.IP1.IP1 --dns IP2.IP2.IP2.IP2 --dns-search example.com \
       --publish mode=host,target=8000,published=8000 --env DOCKER_HOST=IP.IP.IP.IP:2375 \
       --mount type=bind,source=/var/lib/sss/pipes,destination=/var/lib/sss/pipes \
       --mount type=bind,source=/srv/jupyterhub,destination=/srv/jupyterhub,readonly=false \
       --mount type=bind,source=/etc/jupyterhub,destination=/etc/jupyterhub,readonly=true \
       vroomanj/jupyterhub:latest
```

References:
- [Docker - Getting started with swarm mode](https://docs.docker.com/engine/swarm/swarm-tutorial/)
- [Docker - Manage swarm service networks](https://docs.docker.com/engine/swarm/networking/)
- [Docker - Deploy services to a swarm](https://docs.docker.com/engine/swarm/services/)
- [Docker - Docker swarm mode overlay network security model](https://docs.docker.com/engine/userguide/networking/overlay-security-model/)
- [JupyterHub - Getting started with JupyterHub](http://jupyterhub.readthedocs.io/en/latest/getting-started.html)
- [GitHub - cassinyio/SwarmSpawner](https://github.com/cassinyio/SwarmSpawner)
- [GitHub - jupyterhub/dockerspawner/systemuser](https://github.com/jupyterhub/dockerspawner/tree/master/systemuser)
- [sssd.conf(5) - Linux man page](https://linux.die.net/man/5/sssd.conf)
- [Authenticating a docker container against host’s UNIX accounts](https://jhrozek.wordpress.com/2015/03/31/authenticating-a-docker-container-against-hosts-unix-accounts/)
