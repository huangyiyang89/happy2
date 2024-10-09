import logging
import re
from twocaptcha import TwoCaptcha
import cloudscraper
from .key import twokey

def solve_captcha(account, code) -> bool:
    url = f"https://www.bluecg.net/plugin.php?id=gift:v3&ac={account}&time={code}"
    scraper = cloudscraper.create_scraper()
    scraper.headers["Cache-Control"] = "no-cache"
    print("正在验证：")
    print(url)
    # request main_page
    main_page_text = scraper.get(url).text

    if "連結中沒有輸入正確訊息" in main_page_text:
        print("連結中沒有輸入正確訊息，已验证过")
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
        logging.error(e)
        logging.error("wait for 5 seconds")
        return False


def solve_captcha_v2(account, code) -> bool:
    """_summary_

    Args:
        url (_type_): _description_
    """
    url = f"https://www.bluecg.net/plugin.php?id=gift:v2v&ac={account}&time={code}"
    scraper = cloudscraper.create_scraper()
    scraper.headers["Cache-Control"] = "no-cache"
    print("正在验证：")
    print(url)
    # request main_page
    main_page_text = scraper.get(url).text
    matches = re.findall(r'data-sitekey="([^"]+)"', main_page_text)
    if matches:
        sitekey = matches[0]
    else:
        logging.error("not match data-sitekey,%s", url)
        return True

    matches = re.findall(r'updateseccode\(\'([^"]+)\',', main_page_text)
    if matches:
        sid = matches[0]
    else:
        logging.error("not match updateseccode")
        return True

    # solve recaptcha
    capsolver.api_key = key
    solution = capsolver.solve(
        {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": url,
            "websiteKey": sitekey,
        }
    )

    g_recaptcha_response = solution["gRecaptchaResponse"]
    user_agent = solution["userAgent"]
    if not g_recaptcha_response or not user_agent:
        logging.error("capsolver 未响应结果")
        print("capsolver not work")
        return False

    # request captcha image
    captcha_url = "https://www.bluecg.net/misc.php?mod=seccode&idhash=" + sid
    scraper.headers["Referer"] = url
    for i in range(5):
        captcha_response = scraper.get(captcha_url)
        captcha_image_buffer = BytesIO(captcha_response.content)
        img = Image.open(captcha_image_buffer)
        max_duration = 0
        image_bytes_buffer = BytesIO()
        for frame in ImageSequence.Iterator(img):
            duration = frame.info["duration"]
            if duration > max_duration:
                image_bytes_buffer.seek(0)
                image_bytes_buffer.truncate()
                frame.save(image_bytes_buffer, format="PNG")
                max_duration = duration
        # recognize captcha image
        verifycode = classification(image_bytes_buffer)
        checked_res = scraper.get(
            f"https://www.bluecg.net/misc.php?mod=seccode&action=check&inajax=1&modid=plugin::gift&secverify={verifycode}"
        ).text

        if "succeed" in checked_res:
            break
        if i == 4:
            logging.error("验证码5次未能识别")
            return False
    # post verify
    data = {
        "g-recaptcha-response": g_recaptcha_response,
        "seccodehash": sid,
        "seccodemodid": "plugin::gift",
        "seccodeverify": verifycode,
        "submit": "",
    }

    res = scraper.post(url, data=data)
    return True 
