import asyncio

RATE_LIMIT_SIGNALS = [
    'session expired',
    'session invalid',
    'unable to progress',
    'try again in one hour',
    'unable to progress with your request',
]


async def is_expired(page):
    try:
        text = await page.inner_text('body')
    except Exception:
        return False
    if '/page-not-found' in page.url:
        return True
    return any(s in text.lower() for s in RATE_LIMIT_SIGNALS)


async def handle_expired(page):
    if not await is_expired(page):
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
