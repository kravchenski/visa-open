import os
import asyncio

from utils import is_loader_hide


async def fill_form(page):
    try:
        input_xpath = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[10]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        first_name_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[6]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        last_name_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[7]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        sex_dropdown_path = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[8]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        sex_xpath = f'xpath=//span[contains(text(),"{os.environ["sex"]}")]'
        nationality_dropbox_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[9]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
        nationality_xpath = f'xpath=//span[contains(text(),"{os.environ["nationality"]}")]'
        passport_year_xpath = f'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[11]/div/div/div/app-ngb-datepicker/div/div[2]/input'
        country_code_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[1]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        phone_number_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[14]/div/div/div[2]/div[2]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        email_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div/app-dynamic-control[15]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
        button_submit_text_xpath = 'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button/span[2]'
        await asyncio.sleep(2)
        await is_loader_hide(page)
        await asyncio.sleep(30)

        await page.locator(first_name_xpath).fill(os.environ['first_name'])
        await page.locator(last_name_xpath).fill(os.environ['last_name'])
        await page.locator(sex_dropdown_path).click()
        await page.locator(sex_xpath).click()
        await page.locator(nationality_dropbox_xpath).click()
        await page.locator(nationality_xpath).click()
        await asyncio.sleep(2)
        await page.evaluate(f'''
            const input = document.evaluate("{input_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (input) {{
                input.disabled = false;
                input.removeAttribute('disabled');
                input.value = '';
            }}
        ''')
        await asyncio.sleep(2)
        await page.locator(f'xpath={input_xpath}').fill(os.environ['passport_number'])
        await page.locator(passport_year_xpath).fill(os.environ['passport_year'])
        await page.locator(country_code_xpath).fill(os.environ['country_code'])
        await page.locator(phone_number_xpath).fill(os.environ['phone_number'])
        await page.locator(email_xpath).fill(os.environ['your_email'])
        await asyncio.sleep(2)
        await page.locator(button_submit_text_xpath).click()
    except Exception as e:
        print(f"Fill form error: {e}")
