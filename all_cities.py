import datetime
import time

from DrissionPage import ChromiumPage
from DrissionPage.errors import ElementNotFoundError
from audioplayer import AudioPlayer

from config import secret_key_gmail
from form import auth, check_dates
from send_mail import send_mail

# Array of cities
cities = ['Grodno', 'Minsk', 'Gomel', 'Baranovichi', 'Lida', 'Mogilev', 'Brest', 'Pinsk']

while True:
    page = ChromiumPage()
    try:
        print(datetime.datetime.now())
        auth(page)
        time.sleep(7)
        for i in range(len(cities)):
            check_dates(page, cities[i])
            tag_info = page.ele('xpath://div[contains(@class,"border-info mb-0 ng-star-inserted")]').text

            if tag_info != 'Приносим извинения, в настоящий момент нет доступных слотов для записи. Пожалуйста, попробуйте позже':
                print(f"{cities[i]}: " + tag_info)
                print('Send mail....')
                send_mail(secret_key_gmail, cities[i])
                print('Done')
                time.sleep(2)
                print('Play Audio...')
                AudioPlayer("data_audio.wav").play(block=True)
                print('Done')
            else:
                print(f"{cities[i]}: " + tag_info)
        page.close()

    except ElementNotFoundError:
        page.close()
        print('Something went wrong(')
    time.sleep(600)
