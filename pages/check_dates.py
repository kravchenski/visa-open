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

    await human_delay(2, 4)

    if await is_expired(page):
        return False

    print(f"check_dates: url={page.url}")
    await screenshot(page, 'dates_page_loaded')

    city_dropdown = page.locator('mat-select').nth(0)
    visa_dropdown = page.locator('mat-select').nth(1)
    sub_dropdown = page.locator('mat-select').nth(2)
    checkbox = page.locator('input[type="checkbox"]')
    submit_btn = page.locator('button:has-text("Continue")')

    try:
        await city_dropdown.wait_for(state='visible', timeout=15000)
    except Exception:
        print("No mat-select dropdowns found, trying alternative selectors")
        city_dropdown = page.locator('.mat-mdc-select-placeholder:has-text("Application Centre")').locator('..').locator('..')
        visa_dropdown = page.locator('.mat-mdc-select-placeholder:has-text("appointment category")').locator('..').locator('..')
        sub_dropdown = page.locator('.mat-mdc-select-placeholder:has-text("sub-category")').locator('..').locator('..')

    await _select_dropdown(page, city_dropdown, center, 'City')
    if await handle_expired(page):
        return False

    await _select_dropdown(page, visa_dropdown, category, 'Visa')
    if await handle_expired(page):
        return False

    await page.mouse.wheel(0, 600)
    await human_delay(0.5, 1)
    await _select_dropdown(page, sub_dropdown, subcategory, 'Sub')
    if await handle_expired(page):
        return False

    dates = await _read_dates(page)
    print(
        f"City:           {center}\n"
        f"Visa Type:      {category}\n"
        f"Subcategory:    {subcategory}\n"
        f"Available Dates: {dates}\n"
        "------------------------------------------"
    )
    await screenshot(page, 'dates_check')

    await _enable_submit(page)
    await human_delay(0.5, 1)

    if await checkbox.count() > 0:
        try:
            await checkbox.first.check(force=True)
        except Exception:
            try:
                await checkbox.first.click(force=True)
            except Exception:
                pass
    await human_delay(0.5, 1)

    if await handle_expired(page):
        return False

    try:
        await submit_btn.wait_for(state='visible', timeout=10000)
        await submit_btn.click()
    except Exception:
        try:
            await submit_btn.click(force=True)
        except Exception:
            await page.evaluate("""() => {
                const btn = document.querySelector('button.btn-primary, button[type="submit"]');
                if (btn) { btn.disabled = false; btn.removeAttribute('disabled'); btn.click(); }
            }""")

    await human_delay(3, 6)
    return True


async def _select_dropdown(page, dropdown, option_text, label=''):
    try:
        await dropdown.wait_for(state='visible', timeout=10000)
    except Exception:
        print(f"{label} dropdown not visible")
        return
    await dropdown.click()
    await human_delay(0.5, 1)
    if await handle_expired(page):
        return False

    option = page.locator(f'xpath=//mat-option[normalize-space(.)="{option_text}"]')
    try:
        await option.wait_for(state='visible', timeout=10000)
        await option.click()
    except Exception:
        print(f"{label} option '{option_text}' not found, trying partial match")
        try:
            option = page.locator(f'xpath=//mat-option[contains(normalize-space(.),"{option_text}")]').first
            await option.click()
        except Exception:
            print(f"{label} option click failed completely")

    await wait_for_loader(page)
    await human_delay(1, 2)


async def _read_dates(page):
    for selector in [
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div',
        '.dates-container',
        'xpath=//div[contains(@class,"date")]',
    ]:
        locator = page.locator(selector)
        if await locator.count() > 0:
            try:
                await locator.first.wait_for(state='visible', timeout=10000)
                return await locator.first.text_content()
            except Exception:
                pass
    return "N/A"


async def _enable_submit(page):
    await page.evaluate("""() => {
        document.querySelectorAll('button[disabled]').forEach(btn => {
            if (btn.textContent.includes('Continue') || btn.textContent.includes('Submit')) {
                btn.disabled = false;
                btn.removeAttribute('disabled');
            }
        });
    }""")
