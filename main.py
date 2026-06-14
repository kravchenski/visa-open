import asyncio

from camoufox.async_api import AsyncCamoufox
from camoufox_captcha import solve_captcha
from pages.login import login_to_vfs
from pages.check_dates_for_all_visa_types_for_one_city import check_dates_for_all_visa_types_for_one_city
from pages.fill_form import fill_form
from dotenv import load_dotenv
load_dotenv()


async def clear_browser_state(page):
    context = page.context
    await context.clear_cookies()
    await context.clear_permissions()
    await context.route('**/*', lambda route: route.continue_())
    await context.add_init_script("""(() => {
        try {
            localStorage.clear();
            sessionStorage.clear();
        } catch (error) {}

        try {
            if ('caches' in window) {
                caches.keys().then((cacheNames) => {
                    cacheNames.forEach((name) => caches.delete(name));
                });
            }
        } catch (error) {}

        try {
            if (navigator.serviceWorker) {
                navigator.serviceWorker.getRegistrations().then((registrations) => {
                    registrations.forEach((registration) => registration.unregister());
                });
            }
        } catch (error) {}
    })();""")


async def main():
    async with AsyncCamoufox(
        geoip=True,
        humanize=False,
        i_know_what_im_doing=True,
        config={'forceScopeAccess': True},
    ) as browser:
        page = await browser.new_page()
        await clear_browser_state(page)

        while True:
            try:
                await login_to_vfs(page, solve_captcha)
                await check_dates_for_all_visa_types_for_one_city(page)
                await fill_form(page)
            except Exception as e:
                print(f"Error in loop: {e}")
            await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
