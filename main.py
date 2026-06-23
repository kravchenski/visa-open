import os
import asyncio
from pathlib import Path

from cloakbrowser import launch_persistent_context_async
from dotenv import load_dotenv

from pages.login import login
from pages.check_dates import check_dates
from pages.fill_form import fill_form, FACE_VIDEO
from session import is_expired, handle_expired
from utils import screenshot, human_delay

load_dotenv(override=True)

USER_DATA_DIR = os.environ.get('USER_DATA_DIR', str(Path(__file__).parent / '.browser-profile'))


async def main():
    fails = 0
    while True:
        context = None
        page = None
        try:
            context = await launch_persistent_context_async(
                USER_DATA_DIR,
                geoip=True,
                humanize=True,
                args=[
                    '--use-fake-ui-for-media-stream',
                    '--use-fake-device-for-media-stream',
                    f'--use-file-for-fake-video-capture={FACE_VIDEO}',
                ],
            )
            page = await context.new_page()
            page.on('pageerror', lambda err: None)

            if not await login(page):
                fails += 1
                wait = min(60 * fails, 300)
                print(f"Login failed ({fails}x). Waiting {wait}s...")
                await asyncio.sleep(wait)
                continue

            fails = 0
            print("Login OK, checking dates...")

            if not await check_dates(page):
                print("Dates check failed or session expired, waiting 60s...")
                await asyncio.sleep(60)
                continue

            if not await fill_form(page):
                if await is_expired(page):
                    print("Session expired during form fill, waiting 60s...")
                    await asyncio.sleep(60)
                    continue
                print("Fill form failed, retrying...")
                await asyncio.sleep(20)
                continue

            print("ALL DONE!")
            await screenshot(page, 'all_done_final')
            break
        except Exception as e:
            fails += 1
            wait = min(60 * fails, 300)
            print(f"Error ({fails}x): {e}. Waiting {wait}s...")
            if page:
                await screenshot(page, f'main_error_{fails}')
            await asyncio.sleep(wait)
        finally:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass


if __name__ == '__main__':
    asyncio.run(main())
