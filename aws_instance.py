import boto.ec2

# ################ AWS EC2 SERVER SETUP ################ #

# Connection to the region us-east-1
ec2Conn = boto.ec2.connect_to_region("us-east-1",
									aws_access_key_id = "AKIAJBUWTF6VVAK6KJKA",
									aws_secret_access_key = "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")

# Generated key-pair for the secure connection; .pem file saved to the local directory
KeyPair = ec2Conn.create_key_pair("ece496_key_pair")
KeyPair.save("~/ece496")

# Authorize ping, SSH, and HTTP access to the server
securityGroup = ec2Conn.create_security_group("ece496_security_group", "ece496 project server")

securityGroup.authorize(ip_protocol = 'icmp', from_port = -1, to_port = -1, cidr_ip = '0.0.0.0/0')
securityGroup.authorize('tcp', 22, 22, '0.0.0.0/0')
securityGroup.authorize('tcp', 80, 80, '0.0.0.0/0')

instReservation = ec2Conn.run_instances('ami-88aa1ce0',
										key_name = 'ece496_key_pair',
										security_groups = ['ece496_security_group'],
										instance_type = 't1.micro')
										
instance = instReservation[0].instances[0]

status = instance.status

if status == "running":
	print "Instance is running."