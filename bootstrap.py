import configparser,os,subprocess
import boto3
from botocore.client import Config

def get_object(file):
    response = s3.get_object(
        Bucket=bucket,
        Key=directory+file,
    )
    return response['Body'].read()


role_arn  = os.environ['ROLE_ARN']
bucket    = os.environ['BUCKET']
directory = os.environ['DIRECTORY']
region    = os.environ['REGION']

sts = boto3.client('sts')
new_role = sts.assume_role(
    RoleArn=role_arn,
    RoleSessionName='HAProxySession',
)
access_key_id = new_role['Credentials']['AccessKeyId']
secret_access_key = new_role['Credentials']['SecretAccessKey']
session_token = new_role['Credentials']['SessionToken']

session = boto3.session.Session(aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key,
                                aws_session_token=session_token,
                                region_name=region)

s3 = session.client('s3', config=Config(signature_version='s3v4'))


if not os.path.isdir('/bootstrap'):
        os.mkdir('/bootstrap')
with open('/bootstrap/key.pem', 'wb') as key:
    key.write(get_object('certificate-authority.pem'))
with open('/bootstrap/cert.pem', 'wb') as cert:
    cert.write(get_object('certificate.pem'))
with open('/bootstrap/config.cfg', 'wb') as config:
    config.write(get_object('config.cfg'))
with open('/bootstrap/haproxy.cfg', 'wb') as config:
    config.write(get_object('haproxy.cfg'))

parser = configparser.ConfigParser()
parser.read('/bootstrap/config.cfg')
passphrase = parser['HAPROXY']['passphrase']
if 'client_validation' in parser['HAPROXY']:
    with open('/bootstrap/chain.pem', 'wb') as chain:
        chain.write(get_object('certificate-chain.pem'))
subprocess.call(['openssl rsa -in /bootstrap/key.pem -passin pass:' + passphrase + ' -out /bootstrap/key.pem'], shell=True)

# haproxy crt requires Cert -> Key -> Chain
subprocess.call(['cat /bootstrap/cert.pem /bootstrap/key.pem /bootstrap/chain.pem > /bootstrap/server_cert.pem'], shell=True)
