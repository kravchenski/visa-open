import os
import asyncio
from pathlib import Path

from cloakbrowser import launch_persistent_context_async
from dotenv import load_dotenv

from pages.login import login
from pages.check_dates import check_dates
from pages.fill_form import fill_form
from session import is_expired
from utils import shot

load_dotenv(override=True)
USER_DATA_DIR = os.environ.get('USER_DATA_DIR', str(Path(__file__).parent / '.browser-profile'))


async def main():
    fails = 0
    while True:
        ctx = None
        try:
            ctx = await launch_persistent_context_async(USER_DATA_DIR, geoip=True, humanize=True)
            page = await ctx.new_page()
            page.on('pageerror', lambda _: None)

            if not await login(page):
                fails += 1
                wait = min(60 * fails, 300)
                print(f"Login failed ({fails}x). Sleep {wait}s")
                await asyncio.sleep(wait)
                continue

            fails = 0
            print("Login OK — checking dates")
            if not await check_dates(page):
                print("Dates check failed / expired. Sleep 60s")
                await asyncio.sleep(60)
                continue

            if not await fill_form(page):
                if await is_expired(page):
                    print("Expired during fill_form. Sleep 60s")
                    await asyncio.sleep(60)
                else:
                    print("fill_form failed. Sleep 20s")
                    await asyncio.sleep(20)
                continue

            print("ALL DONE!")
            break

        except Exception as e:
            fails += 1
            wait = min(60 * fails, 300)
            print(f"Error ({fails}x): {e}. Sleep {wait}s")
            try:
                await shot(page, f'main_error_{fails}')
            except Exception:
                pass
            await asyncio.sleep(wait)
        finally:
            if ctx:
                try:
                    await ctx.close()
                except Exception:
                    pass


if __name__ == '__main__':
    asyncio.run(main())
