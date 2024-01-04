import os, sys, shutil, datetime, fnmatch

DJANGO_CERT = os.environ.get('DJANGO_CERT')
MODULE_DIR = os.path.dirname(os.path.abspath(DJANGO_CERT)) + '\\'
sys.path.append(os.path.dirname(MODULE_DIR))

from logs.logger import get_logger

logger = get_logger(__name__, 'win-acme', 'copy_cert')


def copycert():
    work_dir = os.environ.get('WIN_ACME_WORK', '')
    cert_dir = os.environ.get('WIN_ACME_CERT', '')
    arh_dir = work_dir + str(datetime.date.today())

    logger.info(f'Started: {work_dir=}, {arh_dir=}, {cert_dir=}')

    shutil.rmtree(arh_dir, ignore_errors=True)
    os.mkdir(arh_dir)

    for file in fnmatch.filter(os.listdir(work_dir), 'rusel.by-???.pem'):
        shutil.move(work_dir + file, arh_dir)
        logger.info(f'moved work_dir->arh_dir: {file}')

    for file in fnmatch.filter(os.listdir(work_dir), '*.txt'):
        shutil.move(work_dir + file, arh_dir)
        logger.info(f'moved work_dir->arh_dir: {file}')

    for file in fnmatch.filter(os.listdir(cert_dir), 'rusel.by-???.pem'):
        shutil.copy(cert_dir + file, work_dir)
        logger.info(f'copied cert_dir->work_dir: {file}')

    with open(cert_dir + 'rusel.by-chain-only.pem', 'r') as f1:
        lines = f1.readlines()
        with open(work_dir + 'rusel.by-crt.pem', 'a') as f2:
            f2.writelines(lines)
    logger.info(f'{cert_dir}rusel.by-chain-only.pem merget into {work_dir}rusel.by-crt.pem')

    logger.info('Finished')

if __name__ == '__main__':
    copycert()
