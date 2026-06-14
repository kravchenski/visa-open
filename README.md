<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Camoufox-Anti--Detect-F4A460?style=for-the-badge" alt="Camoufox">
  <img src="https://img.shields.io/badge/Cloudflare-Bypass-F48120?style=for-the-badge" alt="Cloudflare">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/github/stars/kravchenski/visa-open?style=for-the-badge&color=yellow" alt="Stars">
</p>

<h1 align="center">Visa Open</h1>

<p align="center">
  <b>Automated visa appointment checker with Cloudflare bypass</b><br>
  <sub>Monitors VFS Global for available dates and auto-fills applications</sub>
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#configuration">Configuration</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#how-it-works">How It Works</a> ·
  <a href="#supported-cities">Cities</a> ·
  <a href="#contact">Contact</a>
</p>

---

## Features

- **Cloudflare Bypass** — Automatically solves Cloudflare Interstitial and Turnstile challenges using [Camoufox](https://camoufox.com/) anti-detect browser + [camoufox-captcha](https://github.com/user/camoufox-captcha)
- **Date Monitoring** — Checks all visa types and subcategories for a selected city every 10 minutes
- **Auto Form Fill** — When an available date is found, automatically fills the application form
- **Async Architecture** — Built on Playwright async API for reliable, non-blocking automation
- **GeoIP Integration** — Matches timezone, locale, and geolocation to proxy exit node for stealth
- **Fingerprint Randomization** — Unique browser fingerprint per session via BrowserForge

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
git clone https://github.com/kravchenski/visa-open.git
cd visa-open

# Using uv (recommended)
uv sync

# Or using pip
pip install .
```

### Setup

1. Copy the environment file and fill in your credentials:

```bash
cp .env.example .env
```

2. Edit `.env` with your VFS Global login and personal details (see [Configuration](#configuration))

3. Run:

```bash
python main.py
```

## Configuration

All configuration is done through the `.env` file.

### Login Credentials

```env
email_login=your@email.com
password_login=your_password
```

Get these from [VFS Global](https://visa.vfsglobal.com/blr/ru/pol/login).

### Personal Details (for auto form fill)

```env
first_name=John
last_name=Doe
sex=Male                    # Male | Female
nationality=POLAND          # UPPERCASE, English
passport_number=AB123456
passport_year=25/12/2025
country_code=375
phone_number=295045955
your_email=your@email.com
birth_day=06/01/2000        # DD/MM/YYYY
```

### Appointment Parameters

```env
city=Grodno
visa_category=National Visa D
visa_subcategory=Other D-visa
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `email_login` | VFS account email | `user@email.com` |
| `password_login` | VFS account password | `pass123` |
| `city` | Target city | `Grodno` |
| `visa_category` | Visa type | `National Visa D` |
| `visa_subcategory` | Visa subcategory | `Other D-visa` |
| `nationality` | Your nationality (UPPERCASE) | `POLAND` |
| `birth_day` | Date of birth (DD/MM/YYYY) | `06/01/2000` |

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ Camoufox  │───▶│ solve_captcha│───▶│ Cloudflare passed │  │
│  │ (Firefox) │    │ (interstitial│    │                   │  │
│  └──────────┘    │  + turnstile)│    └────────┬──────────┘  │
│                  └──────────────┘             │              │
│                                               ▼              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    login_to_vfs()                       │  │
│  │  1. Navigate to VFS login page                          │  │
│  │  2. Solve Cloudflare challenges                         │  │
│  │  3. Click turnstile in iframe                           │  │
│  │  4. Fill email/password                                 │  │
│  │  5. Submit → Dashboard                                  │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         check_dates_for_all_visa_types()                │  │
│  │  For each visa type:                                    │  │
│  │    For each subcategory:                                │  │
│  │      → Select city/type/subcategory                     │  │
│  │      → Enter birth date                                 │  │
│  │      → Read available dates                             │  │
│  │      → Print results                                    │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    fill_form()                          │  │
│  │  If dates found → auto-fill application form            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                             │
│                    ↻ Repeat every 60s                        │
└─────────────────────────────────────────────────────────────┘
```

## Supported Cities

| City | National Visa D | Schengen Visa C |
|------|:---:|:---:|
| Baranovichi | `Driver D-visa` · `Other D-visa` · `Work D-visa` · `Work D-visa krome Brest oblast` | `Other C Visa` |
| Brest | `Driver D-visa` · `Other D-visa` · `Work D-visa` · `Work D-visa krome Brest oblast` | `Other C Visa` |
| Gomel | `Driver D-visa` · `Other D-visa` | `Visits C-Visa` |
| Grodno | `Other D-visa` · `Work D-visa` · `Postal D-visa` | `Other C Visa` |
| Lida | `Other D-visa` · `Work D-visa` · `Postal D-visa` | — |
| Minsk | `Other D-visa` · `Driver D-visa` · `Postal D-visa` | `Other C Visa` · `Visits C-Visa` |
| Mogilev | `Driver D-visa` · `Other D-visa` | `Visits C-Visa` |
| Pinsk | `Driver D-visa` · `Other D-visa` · `Work D-visa` · `Work D-visa krome Brest oblast` | `Other C Visa` |

## Project Structure

```
visa-open/
├── main.py              # Entry point — AsyncCamoufox browser loop
├── pages/
│   ├── login.py         # VFS login + Cloudflare bypass
│   ├── check_dates_...  # Date checking for all visa types
│   └── fill_form.py     # Auto form filler
├── utils/
│   └── check_elements/
│       └── is_loader_hide.py  # Async loader state checker
├── .env.example         # Configuration template
├── pyproject.toml       # Dependencies & build config
└── README.md
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Browser | [Camoufox](https://camoufox.com/) (Firefox anti-detect) |
| Automation | [Playwright](https://playwright.dev/python/) (async API) |
| Captcha Solver | [camoufox-captcha](https://github.com/user/camoufox-captcha) |
| Fingerprinting | [BrowserForge](https://github.com/nickthecook/browserforge) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer

This project is for **educational purposes only**. Use at your own risk and in accordance with VFS Global's terms of service. The authors are not responsible for any misuse.

## Contact

<p align="center">
  <a href="https://t.me/kravchenski"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://discordapp.com/users/893778320410419280"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
</p>

---

<p align="center">
  Made with ❤️ for the visa appointment struggle
</p>
