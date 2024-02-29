import time

from DrissionPage._functions.keys import Keys
from config import first_name, last_name, sex, passport_number, passport_year, country_code, phone_number, \
    your_email, email_login, password_login, nationality, visa_subcategory, visa_category,birth_day,identification_number


def auth(page):
    page.get('https://visa.vfsglobal.com/blr/ru/pol/login')

    page.ele('xpath://*[@id="mat-input-0"]').input(email_login)
    page.ele('xpath://*[@id="mat-input-1"]').input(password_login)
    time.sleep(5)
    page.ele('xpath:/html/body/app-root/div/div/app-login/section/div/div/mat-card/form/button').click()
    page.ele(
        'css:body > app-root > div > div > app-dashboard > section.container.py-15.py-md-30.d-block.ng-star-inserted > div > div.row.mb-10.mb-md-25 > div.col-12.col-sm-auto.d-lg-none.ng-star-inserted > button').input(
        Keys.ENTER)


def fill_form(page):
    # form to details
    page.ele('xpath://*[@id="mat-input-2"]').input(identification_number)
    page.ele('xpath://*[@id="mat-input-4"]').input(first_name)
    page.ele('xpath://*[@id="mat-input-5"]').input(last_name)
    time.sleep(1)
    page.ele('xpath://*[@id="mat-select-value-9"]/span').click()
    page.ele(f'xpath://span[contains(text(),"{sex}")]').click()
    page.ele('xpath://*[@id="mat-input-6"]').input(passport_number)
    time.sleep(1)
    page.ele('xpath://*[@id="passportExpirtyDate"]').input(passport_year)
    page.ele('xpath://*[@id="mat-input-7"]').input(country_code)
    time.sleep(1)
    page.ele('xpath://*[@id="mat-input-8"]').input(phone_number)
    page.ele('xpath://*[@id="mat-input-9"]').input(email_login)
    page.ele('xpath:/html/body/app-root/div/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button').click()


def check_dates(page, city):
    page.ele('xpath://*[@id="mat-select-value-1"]/span').click()
    page.ele(f'xpath://span[contains(text(),"Poland Visa Application Center-{city}")]').click()
    time.sleep(7)
    page.ele('xpath://*[@id="mat-select-value-5"]/span').click()
    page.ele(f'xpath://span[contains(text(), "{visa_category}")]').click()
    time.sleep(7)
    page.ele('xpath://*[@id="mat-select-value-3"]/span').click()
    page.ele(f'xpath://span[contains(text(),"{visa_subcategory}")]').click()
    page.scroll.down(600)
    time.sleep(2)
    page.ele('xpath://*[@id="mat-select-value-7"]/span').click()
    page.ele(f'xpath://span[contains(text(),"{nationality}")]').click()
    time.sleep(2)
    page.ele(
        'xpath:/html/body/app-root/div/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[4]/div[2]/input').input(
        birth_day)
