import os, shutil, datetime, fnmatch, requests

work_dir = os.environ.get('WIN_ACME_WORK', '')
cert_dir = os.environ.get('WIN_ACME_CERT', '')

def log(type, name, message):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    info = message.replace(' ', '%20')
    requests.get(f'{api_url}/api/logs/write_event/?device=nuc&app=win-acme&service=cert_copy&type={type}&name={name}&info={info}', headers=headers, verify=verify)

arh_dir = work_dir + str(datetime.date.today())

log('info', 'script', f'Started: {work_dir=}, {arh_dir=}, {cert_dir=}')

shutil.rmtree(arh_dir, ignore_errors=True)
os.mkdir(arh_dir)

for file in fnmatch.filter(os.listdir(work_dir), 'rusel.by-???.pem'):
    shutil.move(work_dir + file, arh_dir)
    log('info', 'script', f'moved work_dir->arh_dir: {file}')

for file in fnmatch.filter(os.listdir(work_dir), '*.txt'):
    shutil.move(work_dir + file, arh_dir)
    log('info', 'script', f'moved work_dir->arh_dir: {file}')

for file in fnmatch.filter(os.listdir(cert_dir), 'rusel.by-???.pem'):
    shutil.copy(cert_dir + file, work_dir)
    log('info', 'script', f'copied cert_dir->work_dir: {file}')

with open(cert_dir + 'rusel.by-chain-only.pem', 'r') as f1:
    lines = f1.readlines()
    with open(work_dir + 'rusel.by-crt.pem', 'a') as f2:
        f2.writelines(lines)
log('info', 'script', f'{cert_dir}rusel.by-chain-only.pem merget into {work_dir}rusel.by-crt.pem')

log('info', 'script', 'Finished')
