import logging
import re
from twocaptcha import TwoCaptcha
import cloudscraper
from .key import twokey
import time
from threading import Lock


lock = Lock()
last_execution_time = 0


def rate_limited(func):
    def wrapper(*args, **kwargs):
        global last_execution_time
        with lock:
            current_time = time.time()
            elapsed_time = current_time - last_execution_time
            if elapsed_time < 10:
                return False
            logging.error("可以开始下次验证")
            last_execution_time = time.time()
        return func(*args, **kwargs)

    return wrapper


@rate_limited
def solve_captcha(account, code) -> bool:
    url = f"https://www.bluecg.net/plugin.php?id=gift:v3&ac={account}&time={code}"
    scraper = cloudscraper.create_scraper(
        captcha={"provider": "2captcha", "api_key": twokey}
    )
    #scraper.headers["Cache-Control"] = "no-cache"
    logging.info(f"正在验证：{url}")
    main_page_text = scraper.get(url).text

    if not main_page_text:
        logging.error("未成功访问网页")
        return False

    if "連結中沒有輸入正確訊息" in main_page_text:
        logging.info(f"連結中沒有輸入正確訊息，已验证：{url}")
        return True

    matches = re.findall(r'data-sitekey="([^"]+)"', main_page_text)
    if matches:
        sitekey = matches[0]
    else:
        logging.error("请求的页面不正确，可能访问过于频繁。%s", url)
        return False

    solver = TwoCaptcha(twokey)
    try:
        result = solver.turnstile(sitekey=sitekey, url=url)
        # solve slider
        slide_res = scraper.post(
            url="https://www.bluecg.net/handle_slide_verify.php",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"action": "validate_slide"},
        )
        # post verify
        data = {
            "cf-turnstile-response": result["code"],
            "submit": "",
        }
        res = scraper.post(url, data=data)
        logging.info("验证成功，等待3秒返回结果：" + url)
        time.sleep(3)
        return True
    except Exception as e:
        logging.error(f"验证异常:{e} \n 5秒后重试")
        return False
