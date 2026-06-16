import asyncio
import random
from pathlib import Path

SHOTS = Path(__file__).parent / 'screenshots'


async def shot(page, name):
    SHOTS.mkdir(exist_ok=True)
    await page.screenshot(path=str(SHOTS / f'{name}.png'))


async def delay(a=1.0, b=3.0):
    await asyncio.sleep(random.uniform(a, b))


async def wait_loader(page, sel='.ngx-overlay', timeout=1000):
    try:
        await page.locator(f'css={sel}').wait_for(state='hidden', timeout=timeout)
    except Exception:
        pass
