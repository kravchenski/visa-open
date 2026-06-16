import os

from utils import delay, wait_loader, shot
from session import is_expired


async def check_dates(page):
    if await is_expired(page):
        return False

    center = os.environ.get('appointment_center', 'Poland Visa Application Center-Grodno')
    category = os.environ.get('appointment_category', 'National D Visa')
    subcategory = os.environ.get('appointment_subcategory', 'D- Karta Polaka')

    await delay(2, 4)
    city_dd = page.locator('mat-select').nth(0)
    visa_dd = page.locator('mat-select').nth(1)
    sub_dd = page.locator('mat-select').nth(2)

    await _select(page, city_dd, center)
    if await is_expired(page): return False
    await _select(page, visa_dd, category)
    if await is_expired(page): return False
    await page.mouse.wheel(0, 600)
    await delay(0.5, 1)
    await _select(page, sub_dd, subcategory)
    if await is_expired(page): return False

    dates = await _read_dates(page)
    print(
        f"City: {center} | Visa: {category} | Sub: {subcategory}\n"
        f"Available dates: {dates}\n------------------------------------------"
    )
    await shot(page, 'dates_check')

    # enable + tick checkbox + click Continue
    await page.evaluate("""() => {
        document.querySelectorAll('button[disabled]').forEach(btn => {
            if (/continue|submit/i.test(btn.textContent)) {
                btn.disabled = false; btn.removeAttribute('disabled');
            }
        });
    }""")
    cb = page.locator('input[type="checkbox"]')
    if await cb.count():
        try:
            await cb.first.check(force=True)
        except Exception:
            try:
                await cb.first.click(force=True)
            except Exception:
                pass

    btn = page.locator('button:has-text("Continue")')
    try:
        await btn.click()
    except Exception:
        try:
            await btn.click(force=True)
        except Exception:
            await page.evaluate("""() => {
                const b = document.querySelector('button.btn-primary, button[type="submit"]');
                if (b) { b.disabled = false; b.click(); }
            }""")
    await delay(3, 6)
    return not (await is_expired(page))


async def _select(page, dropdown, text):
    try:
        await dropdown.wait_for(state='visible', timeout=10000)
    except Exception:
        return
    await dropdown.click()
    await delay(0.5, 1)
    opt = page.locator(f'xpath=//mat-option[normalize-space(.)="{text}"]')
    try:
        await opt.wait_for(state='visible', timeout=10000)
        await opt.click()
    except Exception:
        try:
            await page.locator(f'xpath=//mat-option[contains(normalize-space(.),"{text}")]').first.click()
        except Exception:
            pass
    await wait_loader(page)
    await delay(1, 2)


async def _read_dates(page):
    for sel in (
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div',
        '.dates-container',
        'xpath=//div[contains(@class,"date")]',
    ):
        loc = page.locator(sel)
        if await loc.count():
            try:
                await loc.first.wait_for(state='visible', timeout=10000)
                return await loc.first.text_content()
            except Exception:
                pass
    return "N/A"
