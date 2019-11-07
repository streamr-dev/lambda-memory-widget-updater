import json

import logging
import os
import boto3
import json

CLIENT_CW = None
CLIENT_ASG = None
CLIENT_EC2 = None
__version__ = "0.0.1"
logger = logging.getLogger()


def authenticate_cw(region: str):
    global CLIENT_CW
    if CLIENT_CW is None:
        CLIENT_CW = boto3.client('cloudwatch', region_name=region)
    return CLIENT_CW


def authenticate_asg(region: str):
    global CLIENT_ASG
    if CLIENT_ASG is None:
        CLIENT_ASG = boto3.client('autoscaling', region_name=region)
    return CLIENT_ASG


def authenticate_ec2(region: str):
    global CLIENT_EC2
    if CLIENT_EC2 is None:
        CLIENT_EC2 = boto3.client('ec2', region_name=region)
    return CLIENT_EC2


def get_dashboard(dashboard_name: str) -> object:
    return json.loads(CLIENT_CW.get_dashboard(
        DashboardName=dashboard_name
    ).get("DashboardBody"))


def get_widget_position(dashboard: object) -> int:
    for idx, widget in enumerate(dashboard.get("widgets")):
        if widget.get("properties").get("title") == "Telegraf Memory":
            return idx


def get_namespace(dashboard: object, position: int) -> str:
    return dashboard.get("widgets")[position].get("properties").get("metrics")[1][0]


def get_metric(dashboard: object, position: int) -> object:
    metrics = dashboard.get("widgets")[position].get("properties").get("metrics")
    return metrics[0: 1]


def add_ips(ips: list, metric: list, namespace: str):
    for idx, ip in enumerate(ips):
        metric.append(
            [namespace, "mem_used_percent", "host", "ip-" + str(ip).replace(".", "-"),
             {"id": "m" + str(idx + 1), "stat": "Average"}])
    return metric


def update_dashboard(dashboard: object, metrics: list, position) -> object:
    dashboard.get("widgets")[position].get("properties")["metrics"] = metrics
    return dashboard


def push_dushboard(dashboard_name: str, dashboard_json: object):
    CLIENT_CW.put_dashboard(
        DashboardName=dashboard_name,
        DashboardBody=json.dumps(dashboard_json)
    )


def get_instance_ips(asg_name) -> list:
    ips = []
    ids = []
    response = CLIENT_ASG.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            asg_name
        ],
    )
    instances = response.get("AutoScalingGroups")[0].get("Instances")
    for instance in instances:
        ids.append(instance.get("InstanceId"))

    response = CLIENT_EC2.describe_instances(InstanceIds=ids)
    for instance in response.get("Reservations"):
        ips.append(instance.get("Instances")[0].get("PrivateIpAddress"))

    return ips


def lambda_handler(event, context):
    authenticate_asg("eu-west-1")
    authenticate_ec2("eu-west-1")
    authenticate_cw("eu-west-1")
    dashoard_name = os.getenv('DASHBOARD_NAME')  # None
    asg_name = os.getenv('ASG_NAME')

    logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s: %(message)s',
                        level=logging.INFO)
    logging.info("Starting Memory Wideget Updater")
    dashboard = get_dashboard(dashoard_name)
    position = get_widget_position(dashboard)
    metric = get_metric(dashboard, position)
    namespace = get_namespace(dashboard, position)
    ips = get_instance_ips(asg_name)
    metrics = add_ips(ips, metric, namespace)
    dashboard = update_dashboard(dashboard, metrics, position)
    push_dushboard(dashoard_name, dashboard)
    logging.info("Finished Memory Wideget Updater")

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def main():
    lambda_handler(None, None)


if __name__ == '__main__':
    main()
