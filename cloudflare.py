import asyncio

from utils import shot


async def solve_interstitial(page, attempts=10, delay=15):
    """Wait out / click through the Cloudflare 'Just a moment' page."""
    for _ in range(attempts):
        title = (await page.title()).lower()
        if 'moment' not in title and 'checking' not in title:
            return True
        await _click_cf(page)
        await asyncio.sleep(delay)
    title = (await page.title()).lower()
    return 'moment' not in title


async def solve_turnstile(page, attempts=10, delay=8):
    """Click the Turnstile iframe until a cf-turnstile-response token appears."""
    for _ in range(attempts):
        if await _has_token(page):
            return True
        await _click_turnstile(page)
        await asyncio.sleep(delay)
    return await _has_token(page)


async def _has_token(page):
    inp = page.locator('input[name="cf-turnstile-response"]')
    if await inp.count() and (await inp.first.get_attribute('value')):
        return True
    return False


async def _click_cf(page):
    # 1) click the cf-chl-widget iframe at its center
    widget = page.locator('iframe[id^="cf-chl-widget"]')
    if await widget.count():
        box = await widget.first.bounding_box()
        if box:
            await page.mouse.click(box['x'] + box['width'] / 2,
                                   box['y'] + box['height'] / 2)
            return
    # 2) fallback: click inside the CF frame body
    frame = _cf_frame(page)
    if frame:
        try:
            await frame.locator('body').click(timeout=10000, force=True)
        except Exception:
            pass


async def _click_turnstile(page):
    # 1) locate the turnstile iframe by src/id/data-attr
    iframe = await _find_turnstile_iframe(page)
    if iframe:
        box = await iframe.bounding_box()
        if box:
            x, y = box['x'] + 26, box['y'] + box['height'] / 2
            await page.mouse.move(x, y)
            await asyncio.sleep(0.2)
            await page.mouse.click(x, y)
            await asyncio.sleep(3)
            return
    # 2) fallback: click checkbox inside the CF frame
    frame = _cf_frame(page)
    if not frame:
        return
    try:
        cb = frame.locator('#challenge-stage input[type="checkbox"], label, .cb-i, .mark')
        if await cb.count():
            await cb.first.click(timeout=5000, force=True)
        else:
            body = frame.locator('body')
            box = await body.bounding_box()
            if box:
                await page.mouse.click(box['x'] + 20, box['y'] + box['height'] / 2)
        await asyncio.sleep(3)
    except Exception:
        pass


async def _find_turnstile_iframe(page):
    n = await page.locator('iframe').count()
    for i in range(n):
        el = page.locator('iframe').nth(i)
        try:
            src = await el.get_attribute('src') or ''
            fid = await el.get_attribute('id') or ''
            if 'challenges.cloudflare.com' in src or 'turnstile' in fid or 'cf-chl' in fid:
                return el
        except Exception:
            pass
    container = page.locator('[data-turnstile-widget-id] iframe')
    if await container.count():
        return container.first
    return None


def _cf_frame(page):
    for f in page.frames:
        if 'challenges.cloudflare.com' in f.url:
            return f
    return None
