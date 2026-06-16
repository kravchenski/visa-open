import os
import random
import asyncio
from pathlib import Path

from utils import is_loader_hide

SCREENSHOTS_DIR = Path(__file__).parent.parent / 'screenshots'


async def _screenshot(page, name):
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    await page.screenshot(path=str(SCREENSHOTS_DIR / f'{name}.png'))
    print(f"Screenshot saved: screenshots/{name}.png")


RATE_LIMIT_SIGNALS = [
    'session expired', 'session invalid', 'unable to progress',
    'try again in one hour', 'unable to progress with your request',
]


async def human_delay(min_s=1.0, max_s=3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def is_session_expired(page):
    try:
        text = await page.inner_text('body')
    except Exception:
        return False
    if '/page-not-found' in page.url:
        return True
    return any(s in text.lower() for s in RATE_LIMIT_SIGNALS)


async def handle_session_expired(page):
    if not await is_session_expired(page):
        return False
    print("[429] Session Expired or Invalid detected, waiting 90s...")
    await asyncio.sleep(90)
    try:
        home_link = page.locator('text=Go back to home')
        if await home_link.count() > 0:
            await home_link.click(force=True)
            await asyncio.sleep(5)
    except Exception:
        pass
    return True


async def solve_cloudflare_interstitial(page, max_attempts=10, delay=15):
    for attempt in range(max_attempts):
        if await is_session_expired(page):
            await _screenshot(page, f'cf_expired_attempt_{attempt+1}')
            return False
        title = await page.title()
        if 'moment' not in title.lower() and 'checking' not in title.lower():
            return True

        clicked = False

        iframe_el = page.locator('iframe[id^="cf-chl-widget"]')
        if await iframe_el.count() > 0:
            box = await iframe_el.first.bounding_box()
            if box:
                click_x = box['x'] + box['width'] / 2
                click_y = box['y'] + box['height'] / 2
                print(f"CF attempt {attempt + 1}: clicking iframe element at ({click_x:.0f}, {click_y:.0f})")
                await page.mouse.click(click_x, click_y)
                clicked = True

        if not clicked:
            cf_frame = None
            for f in page.frames:
                if 'challenges.cloudflare.com' in f.url:
                    cf_frame = f
                    break

            if cf_frame:
                print(f"CF attempt {attempt + 1}: clicking frame body")
                try:
                    body = cf_frame.locator('body')
                    await body.click(timeout=10000, force=True)
                    clicked = True
                except Exception as e:
                    print(f"CF click error: {e}")
            else:
                print(f"CF attempt {attempt + 1}: no frame found")

        if not clicked:
            await _screenshot(page, f'cf_no_click_attempt_{attempt+1}')

        await asyncio.sleep(delay)

    await _screenshot(page, 'cf_final_fail')
    title = await page.title()
    return 'moment' not in title.lower()


async def solve_turnstile(page, max_attempts=10, delay=15):
    for attempt in range(max_attempts):
        if await is_session_expired(page):
            await _screenshot(page, f'turnstile_expired_attempt_{attempt+1}')
            return False

        turnstile_input = page.locator('input[name="cf-turnstile-response"]')
        if await turnstile_input.count() > 0:
            val = await turnstile_input.first.get_attribute('value')
            if val:
                print(f"Turnstile token received! (length={len(val)})")
                return True

        widget = page.locator('iframe[id^="cf-chl-widget"]')
        if await widget.count() > 0:
            box = await widget.first.bounding_box()
            if box:
                click_x = box['x'] + 26
                click_y = box['y'] + box['height'] / 2
                print(f"Turnstile attempt {attempt + 1}: clicking iframe at ({click_x:.0f}, {click_y:.0f})")
                await page.mouse.click(click_x, click_y)
                await asyncio.sleep(3)

                if await turnstile_input.count() > 0:
                    val = await turnstile_input.first.get_attribute('value')
                    if val:
                        print(f"Turnstile token received! (length={len(val)})")
                        return True

        cf_frame = None
        for f in page.frames:
            if 'challenges.cloudflare.com' in f.url:
                cf_frame = f
                break

        if cf_frame:
            print(f"Turnstile attempt {attempt + 1}: clicking inside CF frame")
            try:
                checkbox = cf_frame.locator('#challenge-stage input[type="checkbox"], label, .cb-i')
                if await checkbox.count() > 0:
                    await checkbox.first.click(timeout=5000, force=True)
                else:
                    body = cf_frame.locator('body')
                    await body.click(timeout=10000, force=True)
            except Exception as e:
                print(f"Frame click error: {e}")
        else:
            print(f"Turnstile attempt {attempt + 1}: no widget or frame found")

        await _screenshot(page, f'turnstile_attempt_{attempt+1}')
        await asyncio.sleep(delay)

    print("WARNING: Turnstile not solved after all attempts")
    await _screenshot(page, 'turnstile_final_fail')
    return False


async def clear_session(page):
    context = page.context
    await context.clear_cookies()
    await page.evaluate("""() => {
        try { localStorage.clear(); } catch(e) {}
        try { sessionStorage.clear(); } catch(e) {}
    }""")


async def dismiss_cookies(page):
    await asyncio.sleep(2)
    accept_btn = page.locator('#onetrust-accept-btn-handler')
    reject_btn = page.locator('#onetrust-reject-all-handler')
    clicked = False
    for _ in range(3):
        try:
            if await accept_btn.count() > 0:
                await accept_btn.click(timeout=5000, force=True)
                print("Clicked Accept All Cookies")
                clicked = True
                break
            elif await reject_btn.count() > 0:
                await reject_btn.click(timeout=5000, force=True)
                print("Clicked Reject All Cookies")
                clicked = True
                break
        except Exception:
            pass
        await asyncio.sleep(2)

    await page.evaluate("""() => {
        document.querySelectorAll('#onetrust-consent-sdk, #onetrust-group-container, .onetrust-pc-dark-filter, #onetrust-banner-sdk').forEach(el => el.remove());
    }""")
    await asyncio.sleep(1)
    if not clicked:
        print("Cookie buttons not found, SDK removed via JS")


async def login_to_vfs(page):
    email = os.environ['email_login']
    password = os.environ['password_login']

    await page.goto('https://services.vfsglobal.by/blr/en/pol/dashboard', timeout=60000)
    await page.wait_for_load_state(state='domcontentloaded')

    if await handle_session_expired(page):
        return False

    success = await solve_cloudflare_interstitial(page)
    if not success:
        if await handle_session_expired(page):
            return False
        print("Failed to solve Cloudflare interstitial")
        await _screenshot(page, 'login_cf_failed')
        return False

    print("Cloudflare interstitial solved!")
    await human_delay(2, 4)

    await dismiss_cookies(page)
    await human_delay(5, 10)

    if await handle_session_expired(page):
        return False

    if '/page-not-found' in page.url:
        home_link = page.locator('xpath=/html/body/app-root/div/main/div/app-not-found/div/a')
        if await home_link.count() > 0:
            await home_link.click(force=True)
            await human_delay(8, 12)
        if 'login' not in page.url:
            await page.goto('https://services.vfsglobal.by/blr/en/pol/dashboard', timeout=60000)
            await page.wait_for_load_state(state='domcontentloaded')
            await human_delay(2, 4)

    if await handle_session_expired(page):
        return False

    await solve_turnstile(page)

    email_input = page.locator('#email')
    await email_input.wait_for(state='visible', timeout=60000)
    await human_delay(1, 3)
    await email_input.fill(email)

    password_input = page.locator('#password')
    await password_input.wait_for(state='visible', timeout=60000)
    await human_delay(0.5, 1.5)
    await password_input.fill(password)

    login_btn = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button'
    )
    await login_btn.wait_for(state='visible', timeout=30000)
    await page.evaluate("""() => {
        const btn = document.querySelector('app-login section div mat-card form button');
        if (btn) {
            btn.disabled = false;
            btn.removeAttribute('disabled');
        }
    }""")
    await human_delay(0.5, 1.5)
    await login_btn.click(force=True)

    await human_delay(6, 10)
    current_url = page.url
    title = await page.title()
    print(f"After login click: url={current_url}, title={title}")

    if await handle_session_expired(page):
        return False

    try:
        await page.wait_for_url('**/dashboard**', timeout=15000)
    except Exception:
        if await handle_session_expired(page):
            return False
        print(f"No dashboard redirect. Current: {page.url}")
        await _screenshot(page, 'login_no_dashboard')
        return False

    print(f"Logged in! URL: {page.url}")

    await page.locator(
        'xpath=/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[2]/div/button/span[2]'
    ).click()

    await is_loader_hide(page)
    return True
