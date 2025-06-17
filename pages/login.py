import os

from DrissionPage._functions.keys import Keys
from utils import is_cloudflare_bypass, is_loader_hide


def login_to_vfs(page):
    try:
        email = os.environ['email_login']
        password = os.environ['password_login']
        page.get(page.base_url)
        ele = page.ele('xpath:/html/body/div[2]/div[2]/div/div/div[2]/div/div/button[1]', timeout=30)
        if ele is not None:
            ele.click()
        page.ele('xpath://*[@id="email"]', timeout=60).input(email)
        page.ele('xpath://*[@id="password"]', timeout=60).input(password)

        is_cloudflare_bypass(page)
        page.ele(
            'xpath:/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button', timeout=60).click()
        page.ele(
            'xpath:/html/body/app-root/div/main/div/app-dashboard/section[1]/div/div[1]/div[2]/button',
            timeout=60).input(
            Keys.ENTER)
        is_loader_hide(page)
    except:
        pass
    # your logic for error handling or retrying can go here
