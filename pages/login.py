import os
import asyncio

from utils import shot, delay, wait_loader
from session import is_expired
from cloudflare import solve_interstitial, solve_turnstile

VFS_URL = 'https://services.vfsglobal.by/blr/en/pol/dashboard'
MAX_RETRIES = 5


async def login(page):
    email, pwd = os.environ['email_login'], os.environ['password_login']

    await page.goto(VFS_URL, timeout=60000)
    await page.wait_for_load_state('domcontentloaded')
    if not await solve_interstitial(page):
        return False
    await delay(1, 2)
    await _dismiss_cookies(page)
    await delay(2, 4)

    if not await _ensure_login_page(page):
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        if not await solve_turnstile(page):
            return False
        await _fill(page, email, pwd)
        await _submit(page)
        await delay(3, 5)
        try:
            await page.wait_for_url('**/dashboard**', timeout=15000)
            break
        except Exception:
            pass
        if await _is_blocked(page):
            print(f"[{attempt}/{MAX_RETRIES}] blocked, recovering...")
            if not await _ensure_login_page(page):
                return False
            if attempt == MAX_RETRIES:
                return False
            await delay(5, 10)
        else:
            await shot(page, 'login_no_dashboard')
            return False
    else:
        return False

    # Click "New Appointment"
    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[2]/div/button/span[2]'
    ).click()
    await delay(3, 6)
    await wait_loader(page)
    return not (await is_expired(page))


async def _is_blocked(page):
    if '/page-not-found' in page.url:
        return True
    return await is_expired(page)


async def _ensure_login_page(page):
    """Recover from page-not-found / rate-limit by clearing state and re-navigating."""
    if '/page-not-found' not in page.url and '/login' in page.url:
        return True
    try:
        await page.context.clear_cookies()
    except Exception:
        pass
    await page.evaluate("""() => {
        try { localStorage.clear(); } catch(e) {}
        try { sessionStorage.clear(); } catch(e) {}
    }""")
    # try the "go home" link first
    home = page.locator('xpath=/html/body/app-root/div/main/div/app-not-found/div/a')
    if await home.count():
        await home.click(force=True)
        await delay(3, 5)
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=30000)
        except Exception:
            pass
    if '/page-not-found' in page.url or '/login' not in page.url:
        await page.goto(VFS_URL, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        await delay(2, 4)
    if not await solve_interstitial(page):
        return False
    await _dismiss_cookies(page)
    await delay(1, 2)
    return '/page-not-found' not in page.url


async def _fill(page, email, pwd):
    for sel, val in (('#email', email), ('#password', pwd)):
        inp = page.locator(sel)
        await inp.wait_for(state='visible', timeout=60000)
        await inp.click()
        await inp.fill('')
        await inp.type(val, delay=50)
        # Angular Material reactive forms need native input/change events
        # to update FormControl value — .type() alone is not enough here.
        await inp.evaluate('el => { el.dispatchEvent(new Event("input", {bubbles: true})); el.dispatchEvent(new Event("change", {bubbles: true})); }')


async def _submit(page):
    btn = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button'
    )
    await btn.wait_for(state='visible', timeout=30000)
    for _ in range(10):
        if not await btn.evaluate('el => el.disabled || el.classList.contains("mat-mdc-button-disabled")'):
            await btn.click()
            return
        await asyncio.sleep(0.5)
    # force via JS
    await page.evaluate("""() => {
        const form = document.querySelector('app-login section div mat-card form');
        if (form) form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        const btn = document.querySelector('app-login button[type="submit"], app-login form button');
        if (btn) { btn.disabled = false; btn.click(); }
    }""")


async def _dismiss_cookies(page):
    await asyncio.sleep(1)
    for sel in ('#onetrust-accept-btn-handler', '#onetrust-reject-all-handler'):
        btn = page.locator(sel)
        if await btn.count():
            try:
                await btn.click(timeout=5000, force=True)
                break
            except Exception:
                pass
    await page.evaluate("""() => {
        document.querySelectorAll('#onetrust-consent-sdk, #onetrust-banner-sdk, .onetrust-pc-dark-filter').forEach(el => el.remove());
    }""")
