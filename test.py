# import webbrowser


# controller = webbrowser.get('/usr/bin/google-chrome')
# controller.open_new('https://desktop-6k6p7n0/WebRH')


from selenium import webdriver
import time


def start():
    driver = webdriver.Chrome()
    driver.get('https://desktop-6k6p7n0/WebRH/container_webrh.html')
    print(driver.get_cookies())
    time.sleep(5)
    driver.find_element_by_id('changeScreen').clear()
    time.sleep(1)
    driver.find_element_by_id('changeScreen').send_keys('Screen_2')
    driver.find_element_by_xpath(
        "//input[@type='button' and @value='go']").click()
    while True:
        time.sleep(100000000000000)


if __name__ == "__main__":
    start()

# import subprocess
# subprocess.call(['./automate3.sh'])
