<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CloakBrowser-Stealth-6B4C9A?style=for-the-badge" alt="CloakBrowser">
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

- **Cloudflare Bypass** — Automatically solves Cloudflare Interstitial and Turnstile challenges using [CloakBrowser](https://github.com/CloakHQ/CloakBrowser) stealth browser
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

2. Edit `.env` with your VFS Global login and appointment parameters (see [Configuration](#configuration))

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

### Appointment Parameters

```env
appointment_center=Poland Visa Application Center-Grodno
appointment_category=National D Visa
appointment_subcategory=D- Karta Polaka
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `email_login` | VFS account email | `user@email.com` |
| `password_login` | VFS account password | `pass123` |
| `appointment_center` | Appointment center option text | `Poland Visa Application Center-Grodno` |
| `appointment_category` | Appointment category option text | `National D Visa` |
| `appointment_subcategory` | Appointment subcategory option text | `D- Karta Polaka` |

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ CloakBrowser │─▶│ solve_captcha│─▶│ Cloudflare passed │  │
│  │ (Stealth)    │  │ (interstitial│  │                   │  │
│  └──────────────┘  │  + turnstile)│  └────────┬──────────┘  │
│                    └──────────────┘           │              │
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
├── main.py              # Entry point — CloakBrowser persistent context loop
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
| Browser | [CloakBrowser](https://github.com/CloakHQ/CloakBrowser) (stealth Chromium) |
| Automation | [Playwright](https://playwright.dev/python/) (async API) |
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
