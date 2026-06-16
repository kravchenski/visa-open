import random
import asyncio
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).parent / 'screenshots'


async def screenshot(page, name):
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    await page.screenshot(path=str(SCREENSHOTS_DIR / f'{name}.png'))
    print(f"Screenshot saved: screenshots/{name}.png")


async def human_delay(min_s=1.0, max_s=3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def wait_for_loader(page, css_selector='.ngx-overlay', timeout=1000):
    locator = page.locator(f'css={css_selector}')
    try:
        await locator.wait_for(state='hidden', timeout=timeout)
    except Exception:
        pass
