from pyrvision import RvisionAPI
from fastapi import FastAPI, Form 
import uvicorn 
import rvision 
import yaml 
import os

os.chdir('/opt/rvision/kuma_script/kuma_script_master/')

with open('config.yaml', 'r', encoding='utf-8') as f_conf:
    config = yaml.safe_load(f_conf.read())

app = FastAPI()


@app.post('/api/v2/incidents')
async def incident(
        alert_id: str = Form(...),
        kuma_url: str = Form(...),
        company: str = Form(...),
        level: str = Form(...)):

    if company==config['rvision']['tenant_1']['tenant_1_name']:
        RvisionAPI(
        host=config['rvision']['tenant_1']['host'],
        token=config['rvision']['tenant_1']['token'],
        protocol=config['rvision']['protocol'],
        verify=False)

    if company==config['rvision']['tenant_2']['tenant_2_name']:
        RvisionAPI(
        host=config['rvision']['tenant_2']['host'],
        token=config['rvision']['tenant_2']['token'],
        protocol=config['rvision']['protocol'],
        verify=False)

    identifier = rvision.check_alert_id(alert_id)

    if not identifier:
        rvision.create_alert(alert_id, kuma_url, company, level)
    else:
        rvision.update_alert(identifier, alert_id)

    kuma_response = {
        "success": True
    }
    return kuma_response


@app.get('/api/v2/tokens/get_info_by_token')
async def first_response():
    kuma_response = {
        "success": True
    }
    return kuma_response


if __name__ == '__main__':
    uvicorn.run(app, host=config['script']['host'], port=config['script']['port'])
