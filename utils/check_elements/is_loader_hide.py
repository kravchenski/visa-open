from playwright.async_api import TimeoutError as PlaywrightTimeout


async def is_loader_hide(page, css_selector='.ngx-overlay', timeout=1000):
    locator = page.locator(f'css={css_selector}')
    try:
        await locator.wait_for(state='hidden', timeout=timeout)
    except Exception:
        pass
