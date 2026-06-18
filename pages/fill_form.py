import os
import random
import string

from utils import human_delay, wait_for_loader
from session import is_expired, handle_expired

_PASSPORT_FILE_INPUT = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/app-file-upload/div/div/div/div/div/input'
_PASSPORT_UPLOAD_BTN = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[1]/app-file-upload/div/div/div/div/div[2]/div[2]/button[1]'
_CONTINUE_BTN = '/html/body/app-root/div/main/div/app-applicant-details/section/mat-card[2]/app-dynamic-form/div/div/app-dynamic-control/div/div/div[2]/button'

PASSPORT_IMAGE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', '161719708023-1080752971.jpg')


async def fill_form(page):
    if await is_expired(page):
        print("Session expired in fill_form")
        return False

    await human_delay(2, 4)
    await wait_for_loader(page)
    await human_delay(2, 3)

    print("Uploading passport image...")
    await _upload_passport(page, PASSPORT_IMAGE)

    await human_delay(2, 3)
    if await handle_expired(page):
        return False

    print("Scrolling down...")
    await page.mouse.wheel(0, 600)
    await human_delay(1, 2)

    print("Setting passport expiry date...")
    await page.evaluate("""() => {
        const input = document.querySelector('#passportExpirtyDate');
        if (input) {
            input.disabled = false;
            input.removeAttribute('disabled');
            input.removeAttribute('readonly');
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, '11/09/2029');
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""")
    await human_delay(0.5, 1)

    print("Filling phone and email...")
    phone_number = '7' + ''.join(random.choices(string.digits, k=7))
    random_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '@gmail.com'

    phone_input_6 = page.locator('#mat-input-6')
    phone_input_7 = page.locator('#mat-input-7')
    email_input_8 = page.locator('#mat-input-8')

    await phone_input_6.wait_for(state='visible', timeout=10000)
    await phone_input_6.click()
    await phone_input_6.fill('')
    await phone_input_6.type('44', delay=50)
    await phone_input_6.evaluate('el => el.dispatchEvent(new Event("input", {bubbles: true}))')
    await human_delay(0.3, 0.5)

    await phone_input_7.click()
    await phone_input_7.fill('')
    await phone_input_7.type(phone_number, delay=50)
    await phone_input_7.evaluate('el => el.dispatchEvent(new Event("input", {bubbles: true}))')
    await human_delay(0.3, 0.5)

    await email_input_8.click()
    await email_input_8.fill('')
    await email_input_8.type(random_email, delay=50)
    await email_input_8.evaluate('el => el.dispatchEvent(new Event("input", {bubbles: true}))')
    await human_delay(0.5, 1)

    if await handle_expired(page):
        return False

    print("Clicking Continue...")
    continue_btn = page.locator(f'xpath={_CONTINUE_BTN}')
    try:
        await continue_btn.wait_for(state='visible', timeout=10000)
        await continue_btn.click()
    except Exception:
        await continue_btn.click(force=True)

    await human_delay(3, 5)

    print("Confirming same passport modal...")
    modal_btn = page.locator('xpath=/html/body/div[3]/div[2]/div/mat-dialog-container/div/div/app-same-passport-modal/div/mat-dialog-actions/div/div/div/button')
    try:
        await modal_btn.wait_for(state='visible', timeout=10000)
        await modal_btn.click()
    except Exception:
        try:
            await modal_btn.click(force=True)
        except Exception:
            print("Modal button not found, skipping")
    await human_delay(3, 5)

    print("Clicking instructions confirm...")
    instructions_btn = page.locator('xpath=/html/body/app-root/div/main/div/app-fvinstructions/div/div[3]/div[2]/button')
    try:
        await instructions_btn.wait_for(state='visible', timeout=10000)
        await instructions_btn.click()
    except Exception:
        try:
            await instructions_btn.click(force=True)
        except Exception:
            print("Instructions button not found, skipping")
    await human_delay(3, 5)

    print("Bypassing Azure Face SDK verification...")
    await _bypass_face_verification(page, PASSPORT_IMAGE)

    await human_delay(5, 8)

    print(f"fill_form complete, url={page.url}")
    return True


async def _upload_passport(page, image_path):
    file_input = page.locator(f'xpath={_PASSPORT_FILE_INPUT}')
    if await file_input.count() == 0:
        print("Passport file input not found, trying button approach")
        upload_btn = page.locator(f'xpath={_PASSPORT_UPLOAD_BTN}')
        if await upload_btn.count() == 0:
            print("Passport upload button not found either")
            return
        async with page.expect_file_chooser() as fc_info:
            await upload_btn.click(force=True)
        file_chooser = await fc_info.value
        await file_chooser.set_files(image_path)
    else:
        await file_input.set_input_files(image_path)

    await human_delay(2, 4)

    submit_btn = page.locator(f'xpath={_PASSPORT_UPLOAD_BTN}')
    if await submit_btn.count() > 0:
        try:
            await submit_btn.wait_for(state='visible', timeout=5000)
            await submit_btn.click()
        except Exception:
            await submit_btn.click(force=True)
        await human_delay(3, 5)

    print(f"Passport uploaded: {image_path}")


async def _bypass_face_verification(page, image_path):
    try:
        await page.wait_for_load_state(state='domcontentloaded', timeout=30000)
    except Exception:
        pass

    await human_delay(2, 4)

    file_input = page.locator('input[type="file"]')
    if await file_input.count() > 0:
        print(f"Found {await file_input.count()} file input(s), uploading passport...")
        await file_input.first.set_input_files(image_path)
        await human_delay(3, 5)
        print("Passport uploaded to face verification input")
        return

    print("No file input found, trying to find hidden input via JS...")
    found = await page.evaluate(f"""() => {{
        const inputs = document.querySelectorAll('input[type="file"]');
        if (inputs.length > 0) {{
            return true;
        }}
        const allInputs = document.querySelectorAll('input');
        for (const inp of allInputs) {{
            if (inp.type === 'file' || inp.accept && inp.accept.includes('image')) {{
                inp.style.display = 'block';
                inp.style.opacity = '1';
                inp.style.position = 'static';
                inp.style.width = '100px';
                inp.style.height = '100px';
                return true;
            }}
        }}
        return false;
    }}""")

    if found:
        file_input = page.locator('input[type="file"]')
        if await file_input.count() > 0:
            await file_input.first.set_input_files(image_path)
            await human_delay(3, 5)
            print("Passport uploaded via hidden input")
            return

    print("Trying camera bypass via JS...")
    await page.evaluate("""() => {
        const video = document.querySelector('video');
        if (video) {
            const stream = video.srcObject;
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        }
    }""")

    print("Trying file chooser approach on any button...")
    try:
        async with page.expect_file_chooser(timeout=5000) as fc_info:
            buttons = page.locator('button')
            count = await buttons.count()
            for i in range(count):
                btn = buttons.nth(i)
                text = await btn.text_content() or ''
                if any(w in text.lower() for w in ['upload', 'photo', 'camera', 'browse', 'file', 'choose']):
                    print(f"Clicking button: {text.strip()}")
                    await btn.click()
                    break
            else:
                for i in range(count):
                    btn = buttons.nth(i)
                    try:
                        box = await btn.bounding_box()
                        if box and box['width'] > 30:
                            await btn.click()
                            break
                    except Exception:
                        pass
        file_chooser = await fc_info.value
        await file_chooser.set_files(image_path)
        await human_delay(3, 5)
        print("Passport uploaded via file chooser")
    except Exception:
        print("Could not find file chooser, face verification may need manual intervention")
