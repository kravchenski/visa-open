import os
import asyncio

from utils import screenshot, human_delay, wait_for_loader
from session import is_expired, handle_expired
from cloudflare import solve_interstitial, solve_turnstile

VFS_URL = 'https://services.vfsglobal.by/blr/en/pol/dashboard'


async def login(page):
    email = os.environ['email_login']
    password = os.environ['password_login']

    await page.goto(VFS_URL, timeout=60000)
    await page.wait_for_load_state(state='domcontentloaded')

    if await handle_expired(page):
        return False

    if not await solve_interstitial(page):
        if await handle_expired(page):
            return False
        print("Failed to solve Cloudflare interstitial")
        await screenshot(page, 'login_cf_failed')
        return False

    print("Cloudflare interstitial solved!")
    await human_delay(2, 4)

    await _dismiss_cookies(page)
    await human_delay(5, 10)

    if await handle_expired(page):
        return False

    if '/page-not-found' in page.url:
        home_link = page.locator('xpath=/html/body/app-root/div/main/div/app-not-found/div/a')
        if await home_link.count() > 0:
            await home_link.click(force=True)
            await human_delay(8, 12)
        if 'login' not in page.url:
            await page.goto(VFS_URL, timeout=60000)
            await page.wait_for_load_state(state='domcontentloaded')
            await human_delay(2, 4)

    if await handle_expired(page):
        return False

    await solve_turnstile(page)

    await _fill_credentials(page, email, password)
    await _submit_login(page)

    await human_delay(6, 10)
    print(f"After login: url={page.url}, title={await page.title()}")

    if await handle_expired(page):
        return False

    try:
        await page.wait_for_url('**/dashboard**', timeout=15000)
    except Exception:
        if await handle_expired(page):
            return False
        print(f"No dashboard redirect. Current: {page.url}")
        await screenshot(page, 'login_no_dashboard')
        return False

    print(f"Logged in! URL: {page.url}")

    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[2]/div/button/span[2]'
    ).click()

    await wait_for_loader(page)
    return True


async def _fill_credentials(page, email, password):
    email_input = page.locator('#email')
    await email_input.wait_for(state='visible', timeout=60000)
    await human_delay(1, 3)
    await email_input.fill(email)

    password_input = page.locator('#password')
    await password_input.wait_for(state='visible', timeout=60000)
    await human_delay(0.5, 1.5)
    await password_input.fill(password)


async def _submit_login(page):
    btn = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button'
    )
    await btn.wait_for(state='visible', timeout=30000)
    await page.evaluate("""() => {
        const btn = document.querySelector('app-login section div mat-card form button');
        if (btn) {
            btn.disabled = false;
            btn.removeAttribute('disabled');
        }
    }""")
    await human_delay(0.5, 1.5)
    await btn.click(force=True)


async def _dismiss_cookies(page):
    await asyncio.sleep(2)
    accept_btn = page.locator('#onetrust-accept-btn-handler')
    reject_btn = page.locator('#onetrust-reject-all-handler')

    for _ in range(3):
        try:
            if await accept_btn.count() > 0:
                await accept_btn.click(timeout=5000, force=True)
                print("Clicked Accept All Cookies")
                break
            elif await reject_btn.count() > 0:
                await reject_btn.click(timeout=5000, force=True)
                print("Clicked Reject All Cookies")
                break
        except Exception:
            pass
        await asyncio.sleep(2)

    await page.evaluate("""() => {
        document.querySelectorAll('#onetrust-consent-sdk, #onetrust-group-container, .onetrust-pc-dark-filter, #onetrust-banner-sdk').forEach(el => el.remove());
    }""")
    await asyncio.sleep(1)
