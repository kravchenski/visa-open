import os
import asyncio

from utils import is_loader_hide


async def login_to_vfs(page, solve_captcha):
    try:
        email = os.environ['email_login']
        password = os.environ['password_login']

        await page.goto('https://visa.vfsglobal.com/blr/en/pol/login', timeout=60000)
        await page.wait_for_load_state(state='networkidle')

        success = await solve_captcha(
            page,
            captcha_type='cloudflare',
            challenge_type='interstitial',
        )
        if not success:
            print("Failed to solve Cloudflare interstitial")
            return False

        print("Cloudflare interstitial solved!")
        await asyncio.sleep(5)

        await page.evaluate("""() => {
            document.querySelector('.onetrust-pc-dark-filter')?.remove();
            document.querySelector('#onetrust-consent-sdk')?.remove();
        }""")

        if '/page-not-found' in page.url:
            link = page.locator('xpath=/html/body/app-root/div/main/div/app-not-found/div/a')
            await link.click(force=True)
            await asyncio.sleep(10)

        for attempt in range(5):
            cf_frame = None
            for f in page.frames:
                if 'challenges.cloudflare.com' in f.url:
                    cf_frame = f
                    break

            if cf_frame:
                print(f"Turnstile attempt {attempt + 1}: clicking frame...")
                try:
                    await page.evaluate("""() => {
                        document.querySelector('.onetrust-pc-dark-filter')?.remove();
                        document.querySelector('#onetrust-consent-sdk')?.remove();
                    }""")
                    checkbox = cf_frame.locator('input[type=checkbox]')
                    if await checkbox.count() > 0:
                        await checkbox.first.click(timeout=10000, force=True)
                        print("Clicked checkbox!")
                    else:
                        body = cf_frame.locator('body')
                        await body.click(timeout=10000, force=True)
                        print("Clicked body in frame!")
                except Exception as e:
                    print(f"Frame click error: {e}")

                await asyncio.sleep(8)

                turnstile_input = page.locator('input[name="cf-turnstile-response"]')
                if await turnstile_input.count() > 0:
                    val = await turnstile_input.first.get_attribute('value')
                    if val:
                        print("Turnstile token received!")
                        break
            else:
                print(f"Attempt {attempt + 1}: No CF frame, waiting...")
                await asyncio.sleep(5)

        email_input = page.locator('#email')
        await email_input.wait_for(state='visible', timeout=60000)
        await email_input.fill(email)

        password_input = page.locator('#password')
        await password_input.wait_for(state='visible', timeout=60000)
        await password_input.fill(password)

        login_btn = page.locator(
            'xpath=/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button'
        )
        await login_btn.wait_for(state='visible', timeout=30000)
        await page.evaluate("""() => {
            const btn = document.querySelector('app-login section div mat-card form button');
            if (btn) {
                btn.disabled = false;
                btn.removeAttribute('disabled');
            }
        }""")
        await asyncio.sleep(1)
        await login_btn.click()

        await page.wait_for_url('**/dashboard**', timeout=30000)
        print(f"Logged in! URL: {page.url}")

        await page.locator(
            'xpath=/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button'
        ).press('Enter')

        await is_loader_hide(page)
        return True
    except Exception as e:
        print(f"Login error: {e}")
        return False
