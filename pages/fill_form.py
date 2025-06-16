import os
import time

from utils import is_loader_hide


def fill_form(page):
    is_loader_hide(page)
    time.sleep(30)
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[6]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').input(
        os.environ['first_name'])
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[7]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').input(
        os.environ['last_name'])
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[8]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
    page.ele(f'xpath://span[contains(text(),"{os.environ["sex"]}")]').click()
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[9]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
    page.ele(f'xpath://span[contains(text(),"{os.environ["nationality"]}")]').click()
    time.sleep(2)
    page.ele(
        f'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[11]/div/div/div/app-ngb-datepicker/div/div[2]/input').input(
        os.environ['passport_year'])
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[1]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').input(
        os.environ['country_code'])
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[2]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').input(
        os.environ['phone_number'])
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[15]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').input(
        os.environ['your_email'])
    time.sleep(2)
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button/span[2]').click()
