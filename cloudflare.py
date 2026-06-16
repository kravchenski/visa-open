import asyncio

from utils import screenshot


async def solve_interstitial(page, max_attempts=10, delay=15):
    for attempt in range(max_attempts):
        title = await page.title()
        if 'moment' not in title.lower() and 'checking' not in title.lower():
            return True

        clicked = await _click_cf_widget(page)
        if not clicked:
            clicked = await _click_cf_frame(page)

        if not clicked:
            await screenshot(page, f'cf_no_click_{attempt + 1}')

        await asyncio.sleep(delay)

    await screenshot(page, 'cf_final_fail')
    title = await page.title()
    return 'moment' not in title.lower()


async def solve_turnstile(page, max_attempts=10, delay=15):
    for attempt in range(max_attempts):
        if await _has_turnstile_token(page):
            return True

        clicked = await _click_turnstile_widget(page)
        if not clicked:
            clicked = await _click_turnstile_frame(page)

        await screenshot(page, f'turnstile_attempt_{attempt + 1}')
        await asyncio.sleep(delay)

    print("WARNING: Turnstile not solved after all attempts")
    await screenshot(page, 'turnstile_final_fail')
    return False


async def _has_turnstile_token(page):
    inp = page.locator('input[name="cf-turnstile-response"]')
    if await inp.count() > 0:
        val = await inp.first.get_attribute('value')
        if val:
            print(f"Turnstile token received! (length={len(val)})")
            return True
    return False


async def _click_cf_widget(page):
    widget = page.locator('iframe[id^="cf-chl-widget"]')
    if await widget.count() == 0:
        return False
    box = await widget.first.bounding_box()
    if not box:
        return False
    x = box['x'] + box['width'] / 2
    y = box['y'] + box['height'] / 2
    print(f"CF: clicking iframe at ({x:.0f}, {y:.0f})")
    await page.mouse.click(x, y)
    return True


async def _click_cf_frame(page):
    frame = _find_cf_frame(page)
    if not frame:
        print("CF: no frame found")
        return False
    print("CF: clicking frame body")
    try:
        await frame.locator('body').click(timeout=10000, force=True)
        return True
    except Exception as e:
        print(f"CF click error: {e}")
        return False


async def _click_turnstile_widget(page):
    widget = page.locator('iframe[id^="cf-chl-widget"]')
    if await widget.count() == 0:
        return False
    box = await widget.first.bounding_box()
    if not box:
        return False
    x = box['x'] + 26
    y = box['y'] + box['height'] / 2
    print(f"Turnstile: clicking iframe at ({x:.0f}, {y:.0f})")
    await page.mouse.click(x, y)
    await asyncio.sleep(3)
    return await _has_turnstile_token(page)


async def _click_turnstile_frame(page):
    frame = _find_cf_frame(page)
    if not frame:
        print("Turnstile: no frame found")
        return False
    print("Turnstile: clicking inside CF frame")
    try:
        checkbox = frame.locator('#challenge-stage input[type="checkbox"], label, .cb-i')
        if await checkbox.count() > 0:
            await checkbox.first.click(timeout=5000, force=True)
        else:
            await frame.locator('body').click(timeout=10000, force=True)
    except Exception as e:
        print(f"Frame click error: {e}")
    return False


def _find_cf_frame(page):
    for f in page.frames:
        if 'challenges.cloudflare.com' in f.url:
            return f
    return None
