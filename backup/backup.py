from datetime import datetime
from manager import Backup
from secret import params

if __name__ == '__main__':
    x = Backup(params['device'], params, datetime(2022, 7, 11).date(), datetime.today().date())
    x.run(False)
