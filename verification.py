import time

from DrissionPage._pages.chromium_page import ChromiumPage

from config import identification_number, country_code, phone_number

def verification_by_phone_erip(page):
    page.new_tab('https://ticketing.raschet.by/vfs/web/login')
    phone_verification_page = page.get_tab(page.latest_tab)
    phone_verification_page.ele('xpath:/html/body/div[1]/div/form/fieldset/div[1]/input').input(identification_number)
    phone_verification_page.ele('xpath:/html/body/div[1]/div/form/fieldset/div[2]/div/input').input(country_code + phone_number)
    phone_verification_page.ele('xpath://*[@id="buttons"]/button[1]').click()

