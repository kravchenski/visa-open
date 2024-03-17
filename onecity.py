import datetime
import time

from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from audioplayer import AudioPlayer

from checknumbers import has_numbers
from config import secret_key_gmail, city, visa_subcategory
from form import fill_form, auth, check_dates
from send_mail import send_mail
from verification import verification_by_phone_erip

while True:
    page = ChromiumPage()
    try:
        print(datetime.datetime.now())
        auth(page)
        time.sleep(7)
        check_dates(page, city)
        tag_info = page.ele('xpath://div[contains(@class,"border-info mb-0 ng-star-inserted")]').text
        if has_numbers(tag_info):
            print('Send mail....')
            send_mail(secret_key_gmail, city)
            print('Done')
            time.sleep(2)
            print('Play Audio...')
            AudioPlayer("data_audio.wav").play(block=True)
            page.scroll.down(300)
            page.ele(
                'xpath:/html/body/app-root/div/div/app-eligibility-criteria/section/form/mat-card[2]/button').click()
            time.sleep(5)
            fill_form(page)
            verification_by_phone_erip(page)
        else:
            print(tag_info)
            time.sleep(10)
            page.scroll.up(700)
            page.ele('xpath://*[@id="mat-select-value-1"]/span').click()
            page.ele(f'xpath://span[contains(text(),"Poland Visa Application Center-Brest")]').click()
            check_dates(page,city)
    except ElementNotFoundError:
        print('Something went wrong(')
        time.sleep(600)