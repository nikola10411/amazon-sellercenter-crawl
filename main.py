import csv
import time
import pyotp

from dotenv import dotenv_values


import undetected_chromedriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_table_data(browser):
    item_list = []
    table_body = browser.find_element(By.ID, 'tableBody')
    rows = table_body.find_elements(By.TAG_NAME, 'kat-table-row')

    for row in rows:
        product_detail_card = row.find_element(By.CLASS_NAME, 'product-details-card')
        title = product_detail_card.find_element(By.TAG_NAME, 'kat-link').get_attribute('label')
        asin = product_detail_card.find_element(By.CLASS_NAME, 'asin').text.split(' ')[1]
        sku = product_detail_card.find_element(By.CLASS_NAME, 'sku').text.split(' ')[1]
        status_changed_date = row.find_element(By.CLASS_NAME, 'status-change-date').text

        item_list.append({
            'title': title,
            'asin': asin,
            'sku': sku,
            'status_changed_date': status_changed_date
        })

    return item_list

def crawl_outstock_items(username: str, password: str, otp_url: str, retry=1):
    try:
        browser = undetected_chromedriver.Chrome()

        url = 'https://sellercentral.amazon.com'
        browser.get(url)

        login_button_div = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, 'login_pl_pnav_c'))
        )
        time.sleep(3)
        login_button = login_button_div.find_element(By.TAG_NAME, 'a')
        login_button.click()


        username_input_field = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, 'ap_email'))
        )
        time.sleep(5)

        password_input_field = browser.find_element(By.ID, 'ap_password')

        username_input_field.send_keys(username)
        time.sleep(3)

        password_input_field.send_keys(password)
        time.sleep(3)

        sign_in_button = browser.find_element(By.ID, 'signInSubmit')

        sign_in_button.click()

        otp_input_field = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, 'auth-mfa-otpcode'))
        )
        time.sleep(5)

        x = pyotp.parse_uri(otp_url)
        opt_code = x.now()

        otp_input_field.send_keys(opt_code)

        sign_in_button = browser.find_element(By.ID, 'auth-signin-button')

        sign_in_button.click()

        picker_body = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'picker-body'))
        )

        time.sleep(8)

        buttons = picker_body.find_elements(By.CLASS_NAME, 'picker-button')
        for button in buttons:
            button_name = button.find_element(By.CLASS_NAME, 'picker-name').text
            if button_name == 'United States':
                button.click()
                break

        select_account_button = browser.find_element(By.CLASS_NAME, 'picker-switch-accounts-button')
        select_account_button.click()


        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, 'favorite-pages-links-list'))
        )

        time.sleep(5)

        fix_products_url = 'https://sellercentral.amazon.com/fixyourproducts?ref_=myi_ia_vl_fba#'
        browser.get(fix_products_url)

        out_of_stock_option = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, 'left-filter-option-div-AGGREGATED_LISTING_TYPE_OUT_OF_STOCK'))
        )

        out_of_stock_option.click()

        time.sleep(3)

        sort_dropdown = browser.find_element(By.ID, 'sort-dropdown')
        sort_dropdown.click()

        options = browser.execute_script('return arguments[0].shadowRoot.querySelectorAll("kat-option")', sort_dropdown)
        for option in options:
            if option.text == 'Date: Ascending':
                option.click()
                break

        time.sleep(5)



        total_result = []
        for i in range(20):
            table_data = get_table_data(browser)
            total_result.extend(table_data)

            pagination = browser.find_element(By.TAG_NAME, 'kat-pagination')
            next_button = browser.execute_script(
                'return arguments[0].shadowRoot.querySelector("span[part=pagination-nav-right]")', pagination)

            next_button.click()
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'kat-table-row#row-0'))
            )

        return total_result
    except NoSuchElementException as e:
        if retry == 3:
            print("Failed the load the page, Please check your internet connection or there is problem in Amazon side")
            print(e.msg)
            return []
        else:
            print('Could not find element or page is not loaded correctly. Try again now.')
            print(e.msg)
            return crawl_outstock_items(username, password, otp_url, retry + 1)

if __name__ == '__main__':
    config = dotenv_values(".env")
    result = crawl_outstock_items(config['USERNAME'], config['PASSWORD'], config['OTP_URL'])

    keys = result[0].keys()

    filename = 'out_of_stock-' + str(int(time.time() * 1000)) + '.csv'

    with open(filename, 'w', newline='') as output_file:
        csv_writer = csv.DictWriter(output_file, keys)
        csv_writer.writeheader()
        csv_writer.writerows(result)

    print("Finished!")