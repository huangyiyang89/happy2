import logging
import re
from twocaptcha import TwoCaptcha
import cloudscraper
from .key import twokey

def solve_captcha(account, code) -> bool:
    url = f"https://www.bluecg.net/plugin.php?id=gift:v3&ac={account}&time={code}"
    scraper = cloudscraper.create_scraper()
    scraper.headers["Cache-Control"] = "no-cache"
    logging.info(f"正在验证：{url}")
    # request main_page
    main_page_text = scraper.get(url).text

    if "連結中沒有輸入正確訊息" in main_page_text:
        logging.info(f"連結中沒有輸入正確訊息，已验证：{url}")
        return True

    matches = re.findall(r'data-sitekey="([^"]+)"', main_page_text)
    if matches:
        sitekey = matches[0]
    else:
        logging.error("not match data-sitekey,%s", url)
        return True

    solver = TwoCaptcha(twokey)
    try:
        result = solver.turnstile(
            sitekey=sitekey,
            url=url
        )
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
       
        logging.info("验证成功："+url)
        return True
    except Exception as e:
        logging.error(f"验证异常:{e} \n 5秒后重试")
        return False

