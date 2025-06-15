# Visa-Open

__"Visa-Open" is an open-source project that automates the verification of dates on the visa site.__

## Setup

I used Python 3.10 and DrissionPage with version 4.0.4.4.

The following command will pull and install the latest commit from this repository, along with its Python dependencies:

    git clone https://github.com/kravchenski/visa-open.git 

To update the package to the latest version of this repository, please go to my repo and run:

    git pull    

Then, install requirements:

    pip install .

## Configuration

You need to go to `config/.env`.

First, you need to replace this `secret_key_gmail`

HOW TO GET A SECRET KEY FOR YOUR MAIL:

1. Go to [Gmail](https://mail.google.com/)
2. Then click to manage your account.
3. `Security > Two-Step-Verification > Enter Your Password > Password Apps > Enter Your Password > Enter your application name`
4. Copy code(16 letters) remove spaces and insert in `secret_key_gmail` AND DON'T SHARE!!!!

#### .env.example:

```commandline
secret_key_gmail=your_secret_key_here

# FOR FORM PAGE
first_name=your_first_name
last_name=your_last_name
sex=Male #Female
passport_number=KH12313
passport_year=25/02/2025
country_code=375
phone_number=123456780
your_email=example@example.com
email_to=example2@example.com

# FOR LOGIN PAGE
email_login=vfs_test@test.com
password_login=vfsgovfs!
city=Grodno
visa_category=National Visa D
visa_subcategory=Other D-visa
nationality=POLAND
birth_day=06/01/2007
```

If the program finds dates, those parameters will be inserted into the application.

Thirdly, insert  __[VisaGlobal](https://visa.vfsglobal.com/blr/ru/pol/login)__ login and password (DON'T SHARE)

And finally, you need to change __Check dates params(one city)__:

1. City: Available Cities are `Baranovichi, Brest, Gomel, Grodno, Lida, Minsk, Mogilev, Pinsk`.
2. Visa Category:

| City        | Visa Category                      |
|-------------|------------------------------------|
| Baranovichi | `National Visa D, Schengen Visa C` |
| Brest       | `National Visa D, Schengen Visa C` |
| Gomel       | `National Visa D, Schengen Visa C` |
| Grodno      | `National Visa D, Schengen Visa C` |
| Lida        | `National Visa D`                  |
| Minsk       | `National Visa D, Schengen Visa C` |
| Mogilev     | `National Visa D, Schengen Visa C` |
| Pinsk       | `National Visa D, Schengen Visa C` |

3. Visa SubCategory:

| City        | National Visa D                                                                                 |           Schengen Visa C           |
|-------------|-------------------------------------------------------------------------------------------------|:-----------------------------------:|
| Baranovichi | `Driver D-visa`<br/> `Other D-visa` <br/>` Work D-visa `<br/> ` Work D-visa krome Brest oblast` |           `Other C Visa `           |
| Brest       | `Driver D-visa`<br/> `Other D-visa` <br/>` Work D-visa `<br/> ` Work D-visa krome Brest oblast` |           `Other C Visa `           |
| Gomel       | `Driver D-visa`<br/> `Other D-visa`                                                             |          `Visits C-Visa `           |
| Grodno      | `Other D-visa` <br/>` Work D-visa ` <br/> `Postal D-visa`                                       |           `Other C Visa `           |
| Lida        | `Other D-visa` <br/>` Work D-visa ` <br/> `Postal D-visa`                                       |                 `-`                 |
| Minsk       | `Other D-visa` <br/> `Driver D-visa` <br/> `Postal D-visa`                                      | `Other C Visa`<br/>`Visits C-Visa ` |
| Mogilev     | `Driver D-visa`<br/> `Other D-visa`                                                             |          `Visits C-Visa `           |
| Pinsk       | `Driver D-visa`<br/> `Other D-visa` <br/>` Work D-visa `<br/> ` Work D-visa krome Brest oblast` |           `Other C Visa `           |

4. Your nationality:

    For example _(write UPPERCASE and in English!!!)_: `BELARUS`, `UKRAINE`, `RUSSIA`,`POLAND` and etc.
5. Your Birthday example (day/month/year): `26/02/2000`


## Usage
Run the script via command that checks dates in a specific city:

     python main.py



## Convert to EXE
Run command:

    python -m auto_py_to_exe
Next, you should choose which file you want to convert:

- **OneCity**
1. Choose `main.py` for Script Location
2. Choose `One File`
3. Choose `Consoled Based`
4. Choose Icon(if you want)
5. In Additional Files, you need to add folders:
   `config/`,`pages/`,`utils/`
6. Click Button `Convert .PY TO EXE` and waiting
7. After that, you need go to output directory and run your personal exe)


- **All Cities**
1. Choose `all_cities.py` for Script Location
2. Choose `One File`
3. Choose `Consoled Based`
4. Choose Icon(if you want)
5. In Additional Files, you need to add files:
   `config.py`,`form.py`,`send_mail.py`
6. Click Button `Convert .PY TO EXE` and waiting
7. After that, you need go to output directory and run your personal exe)

## Some Notes
- If you want to convert py to exe, **`you need to find audio or choose standard, rename your audio to data_audio.wav, then replace audio in that directory which located your exe`**
- Scripts(`main.py`) repeat after every 10 minutes.
## Contact

[Telegram](https://t.me/kravchenski)<br/>
[Discord](https://discordapp.com/users/893778320410419280)