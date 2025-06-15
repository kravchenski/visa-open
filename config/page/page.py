import DrissionPage
from dotenv import load_dotenv


class VisaOpenPage:
    @staticmethod
    def create(mode=None, base_url='https://visa.vfsglobal.com/blr/ru/pol/dashboard'):
        if mode == "incognito":
            options = DrissionPage.ChromiumOptions()
            options.incognito()
            page = DrissionPage.ChromiumPage(addr_or_opts=options)
        else:
            page = DrissionPage.ChromiumPage()

        load_dotenv('config/.env')
        page.base_url = base_url
        page.clear_cache()
        return page
