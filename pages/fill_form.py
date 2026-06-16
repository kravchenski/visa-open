import os

from utils import delay, wait_loader
from session import is_expired

_BASE = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/form/app-dynamic-form/div/div'
_UPLOAD_XP = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/app-file-upload/div/div/div/div/div/button'


def _input(n):
    return f'{_BASE}/app-dynamic-control[{n}]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'


async def fill_form(page):
    if await is_expired(page):
        return False
    await delay(1, 2)
    await wait_loader(page)
    await delay(3, 5)

    await page.locator(f'xpath={_input(6)}').fill(os.environ['first_name'])
    await delay(0.3, 0.8)
    await page.locator(f'xpath={_input(7)}').fill(os.environ['last_name'])
    await delay(0.3, 0.8)

    await _dropdown(page, 8, os.environ['sex'])
    if await is_expired(page): return False
    await _dropdown(page, 9, os.environ['nationality'])
    if await is_expired(page): return False

    # passport number (input is sometimes disabled — enable first)
    pp = _input(10)
    await page.evaluate(f'''() => {{
        const i = document.evaluate("{pp}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (i) {{ i.disabled = false; i.removeAttribute('disabled'); i.value = ''; }}
    }}''')
    await page.locator(f'xpath={pp}').fill(os.environ['passport_number'])
    await delay(0.3, 0.8)

    await page.locator(
        f'xpath={_BASE}/app-dynamic-control[11]/div/div/div/app-ngb-datepicker/div/div[2]/input'
    ).fill(os.environ['passport_year'])
    await delay(0.3, 0.8)

    phone_base = f'{_BASE}/app-dynamic-control[14]/div/div/div[2]'
    await page.locator(f'xpath={phone_base}/div[1]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').fill(os.environ['country_code'])
    await delay(0.3, 0.8)
    await page.locator(f'xpath={phone_base}/div[2]/app-input-control/div/mat-form-field/div[1]/div/div[2]/input').fill(os.environ['phone_number'])
    await delay(0.3, 0.8)

    await page.locator(
        f'xpath={_BASE}/app-dynamic-control[15]/div/div/div/app-input-control/div/mat-form-field/div[1]/div/div[2]/input'
    ).fill(os.environ['your_email'])
    await delay(0.5, 1.5)
    if await is_expired(page): return False

    img = os.environ.get('passport_image', '')
    if img and os.path.isfile(img):
        await _upload_passport(page, img)
    if await is_expired(page): return False

    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button'
    ).click(force=True)
    return True


async def _dropdown(page, idx, text):
    await page.locator(
        f'xpath={_BASE}/app-dynamic-control[{idx}]/div/div/div/app-dropdown/div/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span'
    ).click()
    await delay(0.3, 0.8)
    await page.locator(f'xpath=//span[contains(text(),"{text}")]').click()
    await delay(0.3, 0.8)


async def _upload_passport(page, image_path):
    btn = page.locator(f'xpath={_UPLOAD_XP}')
    if not await btn.count():
        return
    async with page.expect_file_chooser() as fc:
        await btn.click(force=True)
    await fc.value.set_files(image_path)
    await delay(2, 4)
