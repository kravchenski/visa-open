import os

from utils import human_delay, wait_for_loader, screenshot
from session import is_expired, handle_expired


def xpath_text_equals(text):
    escaped_text = text.replace('"', '\\"')
    return f'xpath=//span[normalize-space(.)="{escaped_text}"]'


async def check_dates(page):
    center = os.environ.get('appointment_center', 'Poland Visa Application Center-Grodno')
    category = os.environ.get('appointment_category', 'National D Visa')
    subcategory = os.environ.get('appointment_subcategory', 'D- Karta Polaka')

    if await is_expired(page):
        print("Session expired before dates check")
        return False

    city_dropdown = page.locator('xpath=//*[@id="mat-select-0"]')
    city_option = page.locator(xpath_text_equals(center)).first
    visa_dropdown = page.locator('xpath=//*[@id="mat-select-2"]')
    visa_option = page.locator(xpath_text_equals(category)).first
    sub_dropdown = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span')
    sub_option = page.locator(xpath_text_equals(subcategory)).first
    checkbox = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[4]/mat-checkbox/div/div/input')
    checkbox_container = page.locator(
        'xpath=//mat-checkbox[.//input[@id="mat-mdc-checkbox-0-input"]]')
    birth_input = page.locator(
        'css=body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input')
    submit_xpath = '/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button'

    await human_delay(2, 4)

    await _select_dropdown(page, city_dropdown, city_option)
    await _select_dropdown(page, visa_dropdown, visa_option)

    await page.mouse.wheel(0, 600)
    await human_delay(0.5, 1.5)
    await _select_dropdown(page, sub_dropdown, sub_option)

    if await birth_input.count() > 0:
        try:
            await birth_input.clear(timeout=3000)
            await birth_input.fill(os.environ['birth_day'])
        except Exception:
            pass

    dates = await _read_dates(page)
    city_text = await city_option.text_content()
    visa_text = await visa_option.text_content()
    sub_text = await sub_option.text_content()
    print(
        f"City:           {city_text}\n"
        f"Visa Type:      {visa_text}\n"
        f"Subcategory:    {sub_text}\n"
        f"Available Dates: {dates}\n"
        "------------------------------------------"
    )
    await screenshot(page, 'dates_check')

    await _enable_button(page, submit_xpath)
    await human_delay(0.5, 1.5)
    if await checkbox.count() > 0:
        try:
            await checkbox.check(force=True)
        except Exception:
            await checkbox_container.click(force=True)
    await human_delay(1, 3)

    if await handle_expired(page):
        return False

    await page.locator(f"{submit_xpath}/span[2]").click()
    await human_delay(3, 6)
    return True


async def _select_dropdown(page, dropdown, option):
    await dropdown.click()
    await human_delay(0.5, 1.5)
    if await handle_expired(page):
        return False
    await option.click()
    await wait_for_loader(page)
    await human_delay(1, 3)


async def _read_dates(page):
    locator = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div')
    try:
        await locator.wait_for(state='visible', timeout=15000)
        return await locator.text_content()
    except Exception:
        return "N/A"


async def _enable_button(page, xpath):
    await page.evaluate(f'''
        const button = document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (button) {{
            button.disabled = false;
            button.removeAttribute('disabled');
        }}
    ''')
