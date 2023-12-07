# Amazon SellerCenter Out of stock scraping

----------------------------------------------

## Requirements

- Python 3.10
- Selenium
- Chrome installed on OS

## Installation

### Create virtual environment and active environment

`python3 -m venv venv`

`source ./venv/bin/activate`

### Install packages

`pip install -r requirements.txt`

### Configuration for Amazon SellerCenter Account

Copy `.env.example` file to `.env` and fill the sellercenter account info.

For OTP url you can get it in sellercenter account settings 2FA section.

### Run script

`python main.py`

As the result you will get CSV file which contains title, sku, asin and status change date.
