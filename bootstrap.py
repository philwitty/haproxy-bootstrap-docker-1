import os, subprocess, yaml
from ex_py_commons.session import boto_session
from ex_py_commons.file import read_file_from_url

def get_certificate_list(list, session):
    result = b''
    for cert in list:
        result += read_file_from_url(cert, aws_session=session)
    return result

role_arn   = os.environ.get('ROLE_ARN')
config_url = os.environ['CONFIG_URL']

session = boto_session(role_arn)

config = yaml.load(read_file_from_url(config_url, aws_session=session))

with open('/bootstrap/haproxy.cfg', 'wb') as haproxy_config:
    url = config['HAPROXY']['config']
    haproxy_config.write(read_file_from_url(url, aws_session=session))

cert_path = '/bootstrap/certificate.pem'
with open(cert_path, 'wb') as cert:
    url = config['SSL']['server_certificate']
    cert.write(read_file_from_url(url, aws_session=session))
key_path = '/bootstrap/key.pem'
with open(key_path, 'wb') as key:
    url = config['SSL']['server_certificate_authority']
    key.write(read_file_from_url(url, aws_session=session))
passphrase = config['SSL']['server_certificate_authority_passphrase']

# haproxy doesn't support key with passprhase so remove it
subprocess.call(['openssl', 'rsa', '-in', key_path,
                 '-passin', 'pass:' + passphrase, '-out', key_path])
# haproxy crt requires Cert -> Key -> Chain
subprocess.call(['cat /bootstrap/certificate.pem /bootstrap/key.pem > /bootstrap/server_cert.pem'], shell=True)

if 'server_chain' in config['SSL']:
    with open('/bootstrap/server-certificate-chain.pem', 'wb') as chain:
        chain.write(get_certificate_list(config['SSL']['server_chain'], session))
    subprocess.call(['cat /bootstrap/server-certificate-chain.pem >> /bootstrap/server_cert.pem '], shell=True)

if 'client_authorities' in config['SSL']:
    with open('/bootstrap/client-certificate-authorities.pem', 'wb') as chain:
        chain.write(get_certificate_list(config['SSL']['client_authorities'], session))
