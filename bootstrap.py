import os
from subprocess import check_call
from urllib.parse import urlparse
import yaml
from ex_py_commons.session import boto_session
from ex_py_commons.file import read_file_from_url, \
                               concatenate_files_from_urls


class Default(dict):
    def __missing__(self, key):
        return '{' + key + '}'

role_arn = os.environ.get('ROLE_ARN')
config_url = os.environ['CONFIG_URL']

session = boto_session(role_arn)
config = yaml.load(read_file_from_url(config_url, aws_session=session))
haproxy_config_replacements = Default()

key_path = '/bootstrap/key.pem'
with open(key_path, 'wb') as f:
    url = config['SSL']['server_key']
    f.write(read_file_from_url(url, aws_session=session))
passphrase = config['SSL']['server_key_passphrase']
if urlparse(passphrase).scheme != '':
    passphrase = read_file_from_url(passphrase, aws_session=session).decode()

# haproxy doesn't support key with passprhase so remove it
check_call(['openssl', 'rsa', '-in', key_path,
            '-passin', 'pass:' + passphrase, '-out', key_path])

# haproxy crt requires Cert -> Key -> Chain
crt_path = '/bootstrap/server_cert.pem'
haproxy_config_replacements['crt_path'] = crt_path
with open(crt_path, 'wb') as f:
    url = config['SSL']['server_certificate']
    f.write(read_file_from_url(url, aws_session=session))
    with open(key_path, 'rb') as key:
        f.write(key.read())

if 'server_chain' in config['SSL']:
    server_chain_urls = config['SSL']['server_chain']
    chain = concatenate_files_from_urls(server_chain_urls,
                                        aws_session=session)
    with open(crt_path, 'ab') as f:
        f.write(chain)

client_authorities_path = '/bootstrap/client_certificate_authorities.pem'
haproxy_config_replacements['ca_file_path'] = client_authorities_path
if 'client_authorities' in config['SSL']:
    client_cas_urls = config['SSL']['client_authorities']
    client_cas = concatenate_files_from_urls(client_cas_urls,
                                             aws_session=session)
    with open(client_authorities_path, 'wb') as f:
        f.write(client_cas)

with open('/bootstrap/haproxy.cfg', 'w') as f:
    url = config['HAPROXY']['config']
    haproxy_config = read_file_from_url(url, aws_session=session).decode()
    haproxy_config = haproxy_config.format_map(haproxy_config_replacements)
    f.write(haproxy_config)
