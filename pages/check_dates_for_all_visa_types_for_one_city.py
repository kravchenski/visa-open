import os
import asyncio

from utils import is_loader_hide


async def check_dates_for_all_visa_types_for_one_city(page):
    city_dropdown = page.locator('xpath=//*[@id="mat-select-value-1"]/span')
    city_option = page.locator(f'xpath=//span[contains(text(),"Poland Visa Application Center-{os.environ["city"]}")]')
    visa_type_dropdown = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[2]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span')
    visa_subcategory_dropdown = page.locator(
        'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[3]/mat-form-field/div[1]/div/div[2]/mat-select/div/div[1]/span')
    options_container = page.locator('xpath=/html/body/div[4]/div[2]/div/div')
    birth_date_input = page.locator(
        'css=body > app-root > div > main > div > app-eligibility-criteria > section > form > mat-card.mat-mdc-card.mdc-card.form-card.ng-star-inserted > form > div:nth-child(7) > div.datepicker-div.form-group > input')
    button_selector = '/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button'

    await city_dropdown.click()
    await city_option.click()
    await is_loader_hide(page)

    await visa_type_dropdown.click()
    visa_type_elements = await options_container.locator('xpath=./*').all()

    for i in range(len(visa_type_elements)):
        if i > 0:
            await visa_type_dropdown.click()
        await page.locator(f'xpath=/html/body/div[4]/div[2]/div/div/mat-option[{i + 1}]/span').click()
        await is_loader_hide(page)

        await page.mouse.wheel(0, 600)
        await visa_subcategory_dropdown.click()
        subcategory_elements = await options_container.locator('xpath=./*').all()

        for j in range(len(subcategory_elements)):
            if j > 0:
                await visa_subcategory_dropdown.click()
            await page.locator(f'xpath=/html/body/div[4]/div[2]/div/div/mat-option[{j + 1}]/span').click()
            await is_loader_hide(page)
            await birth_date_input.clear()
            await birth_date_input.fill(os.environ['birth_day'])
            dates_container = await page.locator(
                'xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[5]/div').text_content()
            city_text = await city_option.text_content()
            visa_type_text = await visa_type_elements[i].text_content()
            subcategory_text = await subcategory_elements[j].text_content()
            print(
                f"City:           {city_text}\n"
                f"Visa Type:      {visa_type_text}\n"
                f"Subcategory:    {subcategory_text}\n"
                f"Available Dates: {dates_container}\n"
                "------------------------------------------"
            )

    await page.evaluate(f'''
        const button = document.evaluate("{button_selector}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (button) {{
            button.disabled = false;
            button.removeAttribute('disabled');
        }}
    ''')
    await asyncio.sleep(1)
    await page.locator(
        "xpath=/html/body/app-root/div/main/div/app-eligibility-criteria/section/form/mat-card[2]/button/span[2]"
    ).click()
