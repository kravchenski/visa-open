import os
import asyncio

from utils import is_loader_hide
from pages.login import is_session_expired, handle_session_expired, human_delay, _screenshot


def xpath_text_equals(text):
    escaped_text = text.replace('"', '\\"')
    return f'xpath=//span[normalize-space(.)="{escaped_text}"]'


async def check_dates_for_all_visa_types_for_one_city(page):
    appointment_center = os.environ.get('appointment_center', 'Poland Visa Application Center-Grodno')
    appointment_category = os.environ.get('appointment_category', 'National D Visa')
    appointment_subcategory = os.environ.get('appointment_subcategory', 'D- Karta Polaka')

    if await is_session_expired(page):
        print("Session expired before dates check")
        return False

    city_dropdown = page.locator('xpath=//*[@id="mat-select-0"]')
    city_option = page.locator(xpath_text_equals(appointment_center)).first
    visa_type_dropdown = page.locator('xpath=//*[@id="mat-select-2"]')
    visa_type_option = page.locator(xpath_text_equals(appointment_category)).first
    visa_subcategory_dropdown = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span')
    visa_subcategory_option = page.locator(xpath_text_equals(appointment_subcategory)).first
    terms_checkbox = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[4]/mat-checkbox/div/div/input')
    terms_checkbox_container = page.locator(
        'xpath=//mat-checkbox[.//input[@id="mat-mdc-checkbox-0-input"]]'
    )
    birth_date_input = page.locator(
        'css=body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input')
    button_selector = '/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button'

    await human_delay(2, 4)

    await city_dropdown.click()
    await human_delay(0.5, 1.5)
    if await handle_session_expired(page):
        return False
    await city_option.click()
    await is_loader_hide(page)
    await human_delay(1, 3)

    await visa_type_dropdown.click()
    await human_delay(0.5, 1.5)
    if await handle_session_expired(page):
        return False
    await visa_type_option.click()
    await is_loader_hide(page)
    await human_delay(1, 3)

    await page.mouse.wheel(0, 600)
    await human_delay(0.5, 1.5)
    await visa_subcategory_dropdown.click()
    await human_delay(0.5, 1.5)
    if await handle_session_expired(page):
        return False
    await visa_subcategory_option.click()
    await is_loader_hide(page)
    await human_delay(1, 3)

    if await birth_date_input.count() > 0:
        try:
            await birth_date_input.clear(timeout=3000)
            await birth_date_input.fill(os.environ['birth_day'])
        except Exception:
            pass

    dates_locator = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div')
    try:
        await dates_locator.wait_for(state='visible', timeout=15000)
        dates_container = await dates_locator.text_content()
    except Exception:
        dates_container = "N/A"

    city_text = await city_option.text_content()
    visa_type_text = await visa_type_option.text_content()
    subcategory_text = await visa_subcategory_option.text_content()
    print(
        f"City:           {city_text}\n"
        f"Visa Type:      {visa_type_text}\n"
        f"Subcategory:    {subcategory_text}\n"
        f"Available Dates: {dates_container}\n"
        "------------------------------------------"
    )
    await _screenshot(page, 'passport_error')

    await page.evaluate(f'''
        const button = document.evaluate("{button_selector}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (button) {{
            button.disabled = false;
            button.removeAttribute('disabled');
        }}
    ''')
    await human_delay(0.5, 1.5)
    if await terms_checkbox.count() > 0:
        try:
            await terms_checkbox.check(force=True)
        except Exception:
            await terms_checkbox_container.click(force=True)
    await human_delay(1, 3)

    if await handle_session_expired(page):
        return False

    await page.locator(
        "xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button/span[2]"
    ).click()

    await human_delay(3, 6)
    return True
