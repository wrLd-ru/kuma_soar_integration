from pyrvision import RvisionAPI
from pyrvision.types import Incident, Company
from pyrvision.types.fields import StrField, DateTimeField
import yaml
from kuma import KUMA
import os

os.chdir('/opt/rvision/kuma_script/kuma_script_master')

with open('config.yaml', 'r', encoding='utf-8') as f_conf:
    config = yaml.safe_load(f_conf.read())

#RvisionAPI(
#    host=config['rvision']['host'],
#    token=config['rvision']['token'],
#    protocol=config['rvision']['protocol'],
#    verify=False
#)


class Alert(Incident):
    alert_id = StrField(name=config['alert']['alert_id_tag'])
    kuma_url = StrField(name=config['alert']['kuma_url_tag'])
    firstseen = DateTimeField(name='firstseen')
    lastseen = DateTimeField(name='lastseen')
    device_vendor = StrField(name='device_vendor')


def create_alert(alert_id, kuma_url, company_name, level):
    kuma = KUMA(config['kuma']['host'], config['kuma']['token'])
    kuma_alert = kuma.get_alert(alert_id)

    print(kuma_alert)

    company = Company.objects(name=company_name)[0]
    alert = Alert()
    alert.alert_id = alert_id
    alert.kuma_url = kuma_url
    alert.category = config['alert']['category']
    alert.company = company
    alert.level = level
    alert.description = kuma_alert['name']
    alert.firstseen = kuma_alert.get('firstSeen')
    alert.lastseen = kuma_alert.get('lastSeen')

    kuma_events = kuma.get_events_from_alert(alert_id)
    print(kuma_events)

    alert.device_vendor = kuma_events.get('events',{})[0].get('DeviceVendor')
    alert.push()


def update_alert(identifier, alert_id):
    kuma = KUMA(config['kuma']['host'], config['kuma']['token'])
    kuma_alert = kuma.get_alert(alert_id)

    alert = Alert(identifier=identifier)
    alert.firstseen = kuma_alert.get('firstSeen')
    alert.lastseen = kuma_alert.get('lastSeen')
    alert.push()


def check_alert_id(alert_id):
    incidents = Incident.objects(kuma_alert_id=alert_id)
    if len(incidents) == 0:
        return False
    else:
        return incidents[0].identifier
