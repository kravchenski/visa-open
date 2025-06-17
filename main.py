import time

from config.page import VisaOpenPage
from pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from pages.fill_form import fill_form
from pages.login import login_to_vfs

start = time.time()

page = VisaOpenPage.create(mode='incognito')
if __name__ == '__main__':
    while True:
        page.clear_cache()

        login_to_vfs(page)
        check_dates_for_all_visa_types_for_one_city(page)
        fill_form(page)
        time.sleep(60)
