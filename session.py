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
        url = page.url
    except Exception:
        return False
    if '/page-not-found' in url:
        return True
    try:
        text = await page.inner_text('body', timeout=5000)
    except Exception:
        return False
    return any(s in text.lower() for s in RATE_LIMIT_SIGNALS)


async def handle_expired(page):
    if not await is_expired(page):
        return False
    print("[!] Session Expired or Invalid detected")
    return True
