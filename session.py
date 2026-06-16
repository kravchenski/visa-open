EXPIRED_SIGNALS = (
    'session expired', 'session invalid', 'unable to progress',
    'try again in one hour', 'unable to progress with your request',
)


async def is_expired(page):
    try:
        if '/page-not-found' in page.url:
            return True
        text = await page.inner_text('body', timeout=5000)
    except Exception:
        return False
    return any(s in text.lower() for s in EXPIRED_SIGNALS)
