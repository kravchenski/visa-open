import os
import asyncio

from utils import screenshot, human_delay, wait_for_loader
from session import is_expired, handle_expired
from cloudflare import solve_interstitial, solve_turnstile

VFS_URL = 'https://services.vfsglobal.by/blr/en/pol/dashboard'

MAX_SESSION_RETRIES = 5


async def login(page):
    email = os.environ['email_login']
    password = os.environ['password_login']

    await page.goto(VFS_URL, timeout=60000)
    await page.wait_for_load_state(state='domcontentloaded')

    if not await solve_interstitial(page):
        print("Failed to solve Cloudflare interstitial")
        await screenshot(page, 'login_cf_failed')
        return False

    print("Cloudflare interstitial solved!")
    await human_delay(1, 2)
    await _dismiss_cookies(page)
    await human_delay(2, 4)

    if '/page-not-found' in page.url:
        print("Landed on page-not-found, recovering...")
        if not await _recover_from_not_found(page):
            return False

    for attempt in range(1, MAX_SESSION_RETRIES + 1):
        if '/page-not-found' in page.url or await _is_rate_limited(page):
            print(f"[Retry {attempt}/{MAX_SESSION_RETRIES}] Recovering from rate limit...")
            if not await _recover_from_not_found(page):
                return False

        if not await solve_turnstile(page):
            print("Failed to solve Turnstile")
            await screenshot(page, 'login_turnstile_failed')
            return False

        await _fill_credentials(page, email, password)
        await _submit_login(page)

        await human_delay(3, 5)
        print(f"After login: url={page.url}")

        try:
            await page.wait_for_url('**/dashboard**', timeout=15000)
            print(f"Logged in! URL: {page.url}")
            break
        except Exception:
            pass

        if '/page-not-found' in page.url or await _is_rate_limited(page):
            print(f"[Retry {attempt}/{MAX_SESSION_RETRIES}] Login rejected, recovering...")
            await screenshot(page, f'login_rejected_{attempt}')
            if attempt < MAX_SESSION_RETRIES:
                await human_delay(5, 10)
                continue
            print("Max retries reached")
            return False

        print(f"No dashboard redirect. Current: {page.url}")
        await screenshot(page, 'login_no_dashboard')
        return False
    else:
        return False

    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[2]/div/button/span[2]'
    ).click()

    await human_delay(3, 6)
    await wait_for_loader(page)

    if '/page-not-found' in page.url or await is_expired(page):
        print("Session expired after clicking New Appointment")
        await screenshot(page, 'login_post_click_expired')
        return False

    print(f"After New Appointment click: url={page.url}")
    return True


async def _is_rate_limited(page):
    try:
        url = page.url
    except Exception:
        return False
    if '/page-not-found' in url:
        return True
    try:
        text = await page.inner_text('body', timeout=5000)
    except Exception:
        return False
    signals = [
        'session expired',
        'session invalid',
        'unable to progress',
        'try again in one hour',
    ]
    return any(s in text.lower() for s in signals)


async def _recover_from_not_found(page):
    try:
        await page.context.clear_cookies()
    except Exception:
        pass
    await page.evaluate("""() => {
        try { localStorage.clear(); } catch(e) {}
        try { sessionStorage.clear(); } catch(e) {}
    }""")

    home_link = page.locator('xpath=/html/body/app-root/div/main/div/app-not-found/div/a')
    if await home_link.count() > 0:
        print("Clicking 'Go back to home' link...")
        await home_link.click(force=True)
        await human_delay(5, 10)
        await page.wait_for_load_state(state='domcontentloaded', timeout=30000)
        print(f"After home link, url={page.url}")

    if '/page-not-found' in page.url or '/login' not in page.url:
        print("Direct navigate to VFS URL...")
        await page.goto(VFS_URL, timeout=60000)
        await page.wait_for_load_state(state='domcontentloaded')
        await human_delay(3, 5)
        print(f"After direct nav, url={page.url}")

    if not await solve_interstitial(page):
        print("Failed to solve interstitial during recovery")
        await screenshot(page, 'recovery_cf_failed')
        return False

    await _dismiss_cookies(page)
    await human_delay(2, 4)

    if '/page-not-found' in page.url:
        print("Still on page-not-found after recovery")
        await screenshot(page, 'recovery_still_not_found')
        return False

    print(f"Recovery successful, url={page.url}")
    return True


async def _fill_credentials(page, email, password):
    email_input = page.locator('#email')
    await email_input.wait_for(state='visible', timeout=60000)
    await human_delay(0.5, 1.5)
    await email_input.click()
    await email_input.fill('')
    await email_input.type(email, delay=50)
    await email_input.evaluate('el => el.dispatchEvent(new Event("input", {bubbles: true}))')
    await email_input.evaluate('el => el.dispatchEvent(new Event("change", {bubbles: true}))')

    password_input = page.locator('#password')
    await password_input.wait_for(state='visible', timeout=60000)
    await human_delay(0.3, 0.8)
    await password_input.click()
    await password_input.fill('')
    await password_input.type(password, delay=50)
    await password_input.evaluate('el => el.dispatchEvent(new Event("input", {bubbles: true}))')
    await password_input.evaluate('el => el.dispatchEvent(new Event("change", {bubbles: true}))')


async def _submit_login(page):
    btn = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button'
    )
    await btn.wait_for(state='visible', timeout=30000)

    for _ in range(10):
        is_disabled = await btn.evaluate('el => el.disabled || el.classList.contains("mat-mdc-button-disabled")')
        if not is_disabled:
            break
        await asyncio.sleep(0.5)

    is_disabled = await btn.evaluate('el => el.disabled || el.classList.contains("mat-mdc-button-disabled")')
    if is_disabled:
        print("Button still disabled, trying form submit via JS")
        submitted = await page.evaluate("""() => {
            const form = document.querySelector('app-login section div mat-card form');
            if (form) {
                form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
                return true;
            }
            return false;
        }""")
        if not submitted:
            btn.evaluate('el => { el.disabled = false; el.removeAttribute("disabled"); }')
            await btn.click(force=True)
    else:
        await btn.click()


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
