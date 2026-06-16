import os
import asyncio
from pathlib import Path

from cloakbrowser import launch_persistent_context_async
from pages.login import login_to_vfs, is_session_expired, handle_session_expired, _screenshot
from pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from pages.fill_form import fill_form
from dotenv import load_dotenv
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
            )
            page = await context.new_page()
            page.on('pageerror', lambda err: None)

            logged_in = await login_to_vfs(page)
            if not logged_in:
                fails += 1
                wait = min(60 * fails, 300)
                print(f"Login failed ({fails}x). Waiting {wait}s...")
                await asyncio.sleep(wait)
                continue

            fails = 0
            print("Login OK, checking dates...")

            dates_ok = await check_dates_for_all_visa_types_for_one_city(page)
            if not dates_ok:
                print("Dates check failed or session expired, waiting 90s...")
                await asyncio.sleep(90)
                continue

            form_ok = await fill_form(page)
            if not form_ok:
                if await is_session_expired(page):
                    print("Session expired during form fill, waiting 90s...")
                    await asyncio.sleep(90)
                    continue
                print("Fill form failed, retrying...")
                await asyncio.sleep(30)
                continue

            print("ALL DONE!")
            break
        except Exception as e:
            fails += 1
            wait = min(60 * fails, 300)
            print(f"Error ({fails}x): {e}. Waiting {wait}s...")
            if page:
                await _screenshot(page, f'main_error_{fails}')
            await asyncio.sleep(wait)
        finally:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass


if __name__ == '__main__':
    asyncio.run(main())
