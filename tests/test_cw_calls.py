import json
from unittest import TestCase
from app import authenticate_cw, get_dashboard, get_widget_position, get_metric, add_ips, get_namespace, \
    update_dashboard
import boto3
from moto import mock_ec2
from moto import mock_cloudwatch

JSON_FILE = None
DASHBOARD_NAME = "test-dashboard"
WIDGET_POSITION = 3
IPS = ["10.0.1.1", "10.0.1.2", "10.0.1.3"]
NAMESPACE = "lx-network-nodes"
SINGLE_METRIC = [[{'expression': 'AVG(METRICS())', 'label': 'Memory Average', 'id': 'e1', 'region': 'eu-west-1'}]]
UPDATED_METRICS = [
    [{'expression': 'AVG(METRICS())', 'label': 'Memory Average', 'id': 'e1', 'region': 'eu-west-1'}],
    ['lx-network-nodes', 'mem_used_percent', 'host', 'ip-10-0-1-1', {'id': 'm1', 'stat': 'Average'}],
    ['lx-network-nodes', 'mem_used_percent', 'host', 'ip-10-0-1-2', {'id': 'm2', 'stat': 'Average'}],
    ['lx-network-nodes', 'mem_used_percent', 'host', 'ip-10-0-1-3', {'id': 'm3', 'stat': 'Average'}]]


@mock_cloudwatch
class TestJsonManipulation(TestCase):
    def setUp(self):
        global JSON_FILE
        with open('./tests/test_json/dashboard.json') as json_file:
            JSON_FILE = json.load(json_file)
        client = boto3.client('cloudwatch', region_name="eu-west-1",
                              aws_access_key_id="fake_access_key",
                              aws_secret_access_key="fake_secret_key",
                              )
        client.put_dashboard(
            DashboardName=DASHBOARD_NAME,
            DashboardBody=json.dumps(JSON_FILE)
        )
        authenticate_cw('eu-west-1')

    def tearDown(self):
        pass

    def test_get_dashboard(self):
        dashboard = get_dashboard(DASHBOARD_NAME)
        self.assertEqual(dashboard, JSON_FILE)

    def test_no_dashboard(self):
        dashboard = get_dashboard(DASHBOARD_NAME)
        self.assertEqual(dashboard, JSON_FILE)

    def test_get_widget_postition(self):
        widget_position = get_widget_position(JSON_FILE)
        self.assertEqual(widget_position, WIDGET_POSITION)

    def test_get_metric(self):
        metric = get_metric(JSON_FILE, WIDGET_POSITION)
        self.assertEqual(metric[0][0].get("label"), "Memory Average")

    def test_getnamespace(self):
        self.assertEqual(get_namespace(JSON_FILE, WIDGET_POSITION), NAMESPACE)

    def test_add_ips(self):
        metrics = add_ips(IPS, SINGLE_METRIC, NAMESPACE)
        self.assertEqual(metrics, UPDATED_METRICS)

    def test_update_dashboard(self):
        temp_json = JSON_FILE
        temp_json.get("widgets")[WIDGET_POSITION].get("properties")["metrics"] = UPDATED_METRICS
        self.assertEqual(update_dashboard(JSON_FILE, UPDATED_METRICS, WIDGET_POSITION), temp_json)
