import time

from config.page import VisaOpenPage
from pages.check_dates import check_dates
from pages.login import login_to_vfs

start = time.time()

page = VisaOpenPage.create(mode='incognito')

if __name__ == '__main__':
    login_to_vfs(page)
    check_dates(page)
    print(time.time() - start)
