import os

from utils import human_delay, wait_for_loader
from session import is_expired, handle_expired

_BASE = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div'


def _input(n):
    return f'{_BASE}/app-dynamic-control[{n}]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'


async def fill_form(page):
    if await is_expired(page):
        print("Session expired in fill_form")
        return False

    await human_delay(1, 3)
    await wait_for_loader(page)
    await human_delay(8, 12)

    await page.locator(f'xpath={_input(6)}').fill(os.environ['first_name'])
    await human_delay(0.5, 1.5)
    await page.locator(f'xpath={_input(7)}').fill(os.environ['last_name'])
    await human_delay(0.5, 1.5)

    sex = os.environ['sex']
    await page.locator(f'xpath={_BASE}/app-dynamic-control[8]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
    await human_delay(0.5, 1.5)
    if await handle_expired(page):
        return False
    await page.locator(f'xpath=//span[contains(text(),"{sex}")]').click()
    await human_delay(0.5, 1.5)

    nationality = os.environ['nationality']
    await page.locator(f'xpath={_BASE}/app-dynamic-control[9]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span').click()
    await human_delay(0.5, 1.5)
    if await handle_expired(page):
        return False
    await page.locator(f'xpath=//span[contains(text(),"{nationality}")]').click()
    await human_delay(1, 3)

    passport_input = _input(10)
    await page.evaluate(f'''
        const input = document.evaluate("{passport_input}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (input) {{
            input.disabled = false;
            input.removeAttribute('disabled');
            input.value = '';
        }}
    ''')
    await human_delay(1, 3)
    if await handle_expired(page):
        return False
    await page.locator(f'xpath={passport_input}').fill(os.environ['passport_number'])
    await human_delay(0.5, 1.5)

    passport_year = f'{_BASE}/app-dynamic-control[11]/div/div/div/app-ngb-datepicker/div/div[2]/input'
    await page.locator(f'xpath={passport_year}').fill(os.environ['passport_year'])
    await human_delay(0.5, 1.5)

    phone_base = f'{_BASE}/app-dynamic-control[14]/div/div/div[2]'
    await page.locator(f'xpath={phone_base}/div[1]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').fill(os.environ['country_code'])
    await human_delay(0.5, 1.5)
    await page.locator(f'xpath={phone_base}/div[2]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').fill(os.environ['phone_number'])
    await human_delay(0.5, 1.5)

    await page.locator(f'xpath={_BASE}/app-dynamic-control[15]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').fill(os.environ['your_email'])
    await human_delay(1, 3)

    if await handle_expired(page):
        return False

    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button/span[2]'
    ).click()
    return True
