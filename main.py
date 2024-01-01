import json, requests, string, random, time, io, re
import speech_recognition as sr

from playwright.sync_api import sync_playwright

from pydub import AudioSegment

from bs4 import BeautifulSoup

config = open("./config.json", "r")
settings = json.load(config)

poipoi_token = settings['poipoi_token']
poipoi_sessionhash = settings['poipoi_sessionhash']

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://discord.com',
    'Referer': 'https://discord.com/',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

def get_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(25))  

def remove_string(string:str, remove):
    if type(remove) == str:
        string = string.replace(remove, '')
    elif type(remove) == list:
        for remove_string in remove:
            string = string.replace(remove_string, '')
    return string

def get_email():
    poipoi_session = requests.session()
    poipoi_session.cookies.set('cookie_csrf_token', poipoi_token)
    poipoi_session.cookies.set('cookie_sessionhash', poipoi_sessionhash)
    response = poipoi_session.get(f'https://m.kuku.lu/index.php?action=addMailAddrByManual&by_system=1&csrf_token_check={poipoi_token}&newdomain=cocoro.uk&newuser=')
    email = remove_string(response.text, 'OK:')
    return email

email = get_email()
password = get_password()


def recognize(audio_url: str) -> str:
    seg = AudioSegment.from_file(io.BytesIO(requests.get(audio_url).content))
    seg = seg.set_channels(1)
    seg = seg.set_frame_rate(16000)
    seg = seg.set_sample_width(2)
    audio = io.BytesIO()
    seg.export(audio, 'wav')
    audio.seek(0)
    r = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio = r.record(source)
    return r.recognize_google(audio)

def bytedance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(locale="en-US")
        page = ctx.new_page()
        page.goto("https://proxy2.webshare.io/register")
        print("Creating...")
        page.get_by_test_id("email-input").click()
        page.get_by_test_id("email-input").fill(email)
        print(f"[+] Email: {email}")
        page.get_by_test_id("password-input").click()
        page.get_by_test_id("password-input").fill(password)
        print(f"[+] Password: {password}")
        page.get_by_test_id("signup-button").click()
        page.wait_for_timeout(5500)
        verify = page.frame(name=page.locator('//iframe[starts-with(@src,"https://www.google.com/recaptcha/api2/bframe?")]').get_attribute('name'))
        verify.click('//button[@id="recaptcha-audio-button"]')
        try:
            audio = verify.locator('//a[@class="rc-audiochallenge-tdownload-link"]').get_attribute('href')
            answer = recognize(audio)
            verify.fill('//input[@id="audio-response"]', answer)
            verify.click('//button[@id="recaptcha-verify-button"]')
            page.wait_for_timeout(1000)
            print("[+] Success Recaptcha Bypass")
            print("Verifying...")
            page.wait_for_timeout(7500)
            try:
                poipoi_session = requests.session()
                poipoi_session.cookies.set('cookie_csrf_token', poipoi_token)
                poipoi_session.cookies.set('cookie_sessionhash', poipoi_sessionhash)
                while True:
                    response = poipoi_session.get(f'https://m.kuku.lu/recv._ajax.php?&q={email} Activate Your Webshare Account&csrf_token_check={poipoi_token}')
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if soup.find('span', attrs={'class':'view_listcnt'}).contents[0] == '1':
                        break
                    time.sleep(2)
                soup = BeautifulSoup(response.text, 'html.parser')
                mail_element = soup.find('div', attrs={'class':'main-content'}).find('div', attrs={'style':'z-index:99;'})
                script_element = mail_element.parent.find_all('script')[2]
                parsed_javascript = re.findall(r'\'.*\'', script_element.string)
                num = parsed_javascript[1].split(',')[0].replace('\'', '')
                key = parsed_javascript[1].split(',')[1].replace('\'', '').replace(' ', '')
                
                response = poipoi_session.post('https://m.kuku.lu/smphone.app.recv.view.php', data={'num':num, 'key':key})
                soup = BeautifulSoup(response.text, 'html.parser')
                verify_redirect_url = soup.find('a', href=re.compile("gateway.aquapal.net/jump.php?")).attrs['href']
                print(verify_redirect_url)
                page.goto(verify_redirect_url)
                page.wait_for_timeout(5500)
                print("[+] Success Verify Account!!")
                page.wait_for_timeout(5500)
            except:
                print("[-] Failed Verify Email\nPlease Self")
            print(f"[+] Email: {email}")
            print(f"[+] Password: {password}")
        except Exception as error:
            print(f"[-] Failed Recaptcha Solve {error}")
        browser.close()


if __name__ == "__main__":
    bytedance()
