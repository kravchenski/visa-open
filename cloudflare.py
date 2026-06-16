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


async def solve_turnstile(page, max_attempts=10, delay=8):
    iframe_count = await page.locator('iframe').count()
    print(f"Turnstile: found {iframe_count} iframes on page")
    for i in range(iframe_count):
        el = page.locator('iframe').nth(i)
        try:
            src = await el.get_attribute('src') or ''
            fid = await el.get_attribute('id') or ''
            print(f"  iframe[{i}]: id={fid} src={src[:100]}")
        except Exception:
            pass
    for attempt in range(max_attempts):
        if await _has_turnstile_token(page):
            return True

        clicked = await _click_turnstile_widget(page)
        if not clicked:
            clicked = await _click_turnstile_frame(page)
        if not clicked:
            clicked = await _click_turnstile_js(page)

        await screenshot(page, f'turnstile_attempt_{attempt + 1}')
        print(f"Turnstile attempt {attempt + 1}/{max_attempts}, token={await _has_turnstile_token(page)}")
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
    widget = await _find_turnstile_iframe(page)
    if not widget:
        return False
    box = await widget.bounding_box()
    if not box:
        return False
    x = box['x'] + 26
    y = box['y'] + box['height'] / 2
    print(f"Turnstile: clicking iframe at ({x:.0f}, {y:.0f}), box={box}")
    await page.mouse.move(x, y)
    await asyncio.sleep(0.2)
    await page.mouse.click(x, y)
    await asyncio.sleep(3)
    return await _has_turnstile_token(page)


async def _click_turnstile_frame(page):
    frame = _find_cf_frame(page)
    if not frame:
        print("Turnstile: no CF frame found")
        return False
    print("Turnstile: clicking inside CF frame")
    try:
        checkbox = frame.locator('#challenge-stage input[type="checkbox"], label, .cb-i, .mark')
        if await checkbox.count() > 0:
            print(f"Turnstile: found {await checkbox.count()} checkbox elements")
            await checkbox.first.click(timeout=5000, force=True)
            await asyncio.sleep(3)
            return await _has_turnstile_token(page)
        else:
            body = frame.locator('body')
            if await body.count() > 0:
                box = await body.bounding_box()
                if box:
                    x = box['x'] + 20
                    y = box['y'] + box['height'] / 2
                    print(f"Turnstile: clicking body at ({x:.0f}, {y:.0f})")
                    await page.mouse.move(x, y)
                    await asyncio.sleep(0.2)
                    await page.mouse.click(x, y)
                    await asyncio.sleep(3)
                    return await _has_turnstile_token(page)
    except Exception as e:
        print(f"Frame click error: {e}")
    return False


async def _click_turnstile_js(page):
    try:
        token = await page.evaluate("""() => {
            const inp = document.querySelector('input[name="cf-turnstile-response"]');
            if (inp && inp.value) return inp.value;
            const widget = document.querySelector('[data-turnstile-widget-id]');
            if (widget) {
                const iframe = widget.querySelector('iframe');
                if (iframe) {
                    iframe.contentWindow.postMessage({type: 'click'}, '*');
                }
            }
            return null;
        }""")
        if token:
            print(f"Turnstile token via JS: (length={len(token)})")
            return True
    except Exception as e:
        print(f"Turnstile JS error: {e}")
    return False


async def _find_turnstile_iframe(page):
    iframe_count = await page.locator('iframe').count()
    for i in range(iframe_count):
        el = page.locator('iframe').nth(i)
        try:
            src = await el.get_attribute('src') or ''
            fid = await el.get_attribute('id') or ''
            if 'challenges.cloudflare.com' in src or 'cf-chl' in fid or 'turnstile' in fid:
                print(f"Turnstile: found iframe id={fid} src={src[:100]}")
                return el
        except Exception:
            pass
    container = page.locator('[data-turnstile-widget-id]')
    if await container.count() > 0:
        iframe = container.locator('iframe')
        if await iframe.count() > 0:
            print("Turnstile: found iframe via data-turnstile-widget-id")
            return iframe.first
    for f in page.frames:
        url = f.url
        if 'challenges.cloudflare.com' in url:
            print(f"Turnstile: found CF frame URL: {url[:100]}")
            break
    print("Turnstile: no iframe found")
    return None


def _find_cf_frame(page):
    for f in page.frames:
        if 'challenges.cloudflare.com' in f.url:
            return f
    return None
