import requests
import urllib3
import yaml
import os

urllib3.disable_warnings()

os.chdir('/opt/rvision/kuma_script/kuma_script_master')

with open('config.yaml', 'r', encoding='utf-8') as f_conf:
    config = yaml.safe_load(f_conf.read())


class KUMA:
    def __init__(self, host, token):
        self.base_url = f'https://{host}/api/'
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_alert(self, alert_id):
        url = self.base_url + 'v1/alerts?withAffected'
        params = {'id': alert_id}
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        return response.json()[0]

    def get_events_from_alert(self, alert_id):
        url = self.base_url + 'v1/alerts?withEvents'
        params = {'id': alert_id}
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        return response.json()[0]
