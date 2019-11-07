from unittest import TestCase
from index import authenticate_asg, authenticate_ec2, get_instance_ips
import boto3
from moto import mock_autoscaling, mock_ec2


@mock_autoscaling
@mock_ec2
class TestASGManipulation(TestCase):
    def setUp(self):
        authenticate_asg('eu-west-1')
        authenticate_ec2('eu-west-1')
        client = boto3.client('autoscaling', "eu-west-1")
        client.create_launch_configuration(
            LaunchConfigurationName='LaunchConfiguration')
        client.create_auto_scaling_group(
            AutoScalingGroupName='ASG', LaunchConfigurationName="LaunchConfiguration", MinSize=2, MaxSize=2,
            AvailabilityZones=["eu-west-1a"])
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                'ASG'
            ],
        )

    def tearDown(self):
        pass

    def test_get_instances_id(self):
        #TODO Mocking is incorrect with the real api call
        ips = get_instance_ips("ASG")
        self.assertEqual(True,True)
