import boto3
from botocore.exceptions import NoCredentialsError, ConfigParseError
import time
import os

# Manually specify the AWS credentials file path
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = r'G:\Nimrod\Appleseeds\Projects\Pokemon API\AWS details\credentials'

try:
    # Attempt to retrieve your AWS identity to verify credentials
    client = boto3.client('sts')
    response = client.get_caller_identity()
    print("Credentials are working:", response)
except NoCredentialsError:
    print("No credentials found.")
except ConfigParseError:
    print("Config parsing error. Please check the credentials file format.")

# Specify the region here
region = 'us-west-2'

# Initialize boto3 client for EC2
ec2 = boto3.resource('ec2', region_name=region)

def get_security_group_id(vpc_id, group_name):
    """
    Check if a security group with the given name already exists in the VPC.
    If it exists, return its ID. Otherwise, return None.
    """
    try:
        security_groups = list(ec2.security_groups.filter(Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'group-name', 'Values': [group_name]}
        ]))
        if security_groups:
            return security_groups[0].id
        return None
    except Exception as e:
        print(f"Error checking for existing security group: {e}")
        return None

# Function to create a security group
def create_security_group(vpc_id, security_group_name):
    """
    Create a security group for the EC2 instance.
    The security group allows SSH (port 22) and HTTP (port 80) access.
    """
    # First, check if the security group already exists
    existing_group_id = get_security_group_id(vpc_id, security_group_name)

    if existing_group_id:
        print(f"Security group '{security_group_name}' already exists with ID: {existing_group_id}")
        return existing_group_id  # Use the existing security group ID

    try:
        # Create the security group
        security_group = ec2.create_security_group(
            GroupName='pokemon_app_security_group',
            Description='Security group for the Pokemon app',
            VpcId=vpc_id
        )
        # Add rules to open SSH (port 22) and HTTP (port 80)
        security_group.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=22,
            ToPort=22
        )
        security_group.authorize_ingress(
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80
        )
        print(f'Security group {security_group.id} created with SSH and HTTP access.')
        return security_group.id

    except Exception as e:
        print(f"Error creating security group: {e}")
        return None


# Function to launch an EC2 instance
def launch_ec2_instance(security_group_id, key_name):
    # Define the user-data script for EC2 instance (runs on first boot)
    user_data_script = '''#!/bin/bash
    # Update packages and install necessary software
    sudo apt update -y
    sudo apt install -y python3-pip git python3-tk    # Added git and python3-tk for Tkinter

    # Clone the Pokémon app from GitHub (replace with your repository URL)
    git clone https://github.com/nimix24/Pokemon.git /home/ubuntu/pokemon-app

    # Install required Python packages
    cd /home/ubuntu/pokemon-app
    pip3 install -r requirements.txt

    # Add a message for the user upon login
    echo "Welcome! Your Pokémon app is deployed and ready to use." | sudo tee /etc/motd

    # Run the Pokémon app 
    python3 pokemonAPI.py
    '''

    # Launch the instance
    instance = ec2.create_instances(
        #ImageId='ami-03fa88b353191ee29',  # Ubuntu 22.04 LTS AMI
        ImageId='ami-07c5ecd8498c59db5',  # Amazon linux 2023
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        UserData=user_data_script,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'PokemonAppInstance'}]
        }]
    )

    # Wait for the instance to be in running state
    instance[0].wait_until_running()
    instance[0].reload()

    # Get the Public DNS and Public IP of the instance
    public_dns = instance[0].public_dns_name
    public_ip = instance[0].public_ip_address

    print(f'EC2 instance launched with ID: {instance[0].id}')
    print(f'Public DNS: {public_dns}')
    print(f'Public IP: {public_ip}')
    return instance[0]


def main():
    # Replace with your key pair name
    key_name = 'vockey'

    # Step 1: Get default VPC ID
    try:
        vpc_id = list(ec2.vpcs.filter(Filters=[{'Name': 'isDefault', 'Values': ['true']}]))[0].id
        print(f'Default VPC ID: {vpc_id}')
    except Exception as e:
        print(f"Error retrieving VPC ID: {e}")
        return

    # Step 2: Create Security Group and get its ID
    security_group_id = create_security_group(vpc_id, 'pokemon_app_security_group')
    if security_group_id:
        print(f'Security Group created with ID: {security_group_id}')
    else:
        print('Failed to create security group.')
        return  # Exit the function if security group creation fails

    # Step 3: Launch EC2 Instance
    instance = launch_ec2_instance(security_group_id, key_name)
    print(f'EC2 Instance launched with ID: {instance.id}')


if __name__ == '__main__':
    main()
