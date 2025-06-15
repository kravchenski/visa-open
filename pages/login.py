import os

from utils import is_cloudflare_bypass


def login_to_vfs(page):
    email = os.environ['email_login']
    password = os.environ['password_login']
    page.get(page.base_url)
    page.ele('xpath:/html/body/div[2]/div[2]/div/div/div[2]/div/div/button[1]', timeout=30).click()
    page.ele('xpath://*[@id="email"]', timeout=60).input(email)
    page.ele('xpath://*[@id="password"]', timeout=60).input(password)

    is_cloudflare_bypass(page)
    page.ele(
        'xpath:/html/body/app-root/div/main/div/app-login/section/div/div/mat-card/form/button', timeout=60).click()
