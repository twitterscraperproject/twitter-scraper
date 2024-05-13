from playwright.sync_api import sync_playwright, Playwright
import time
import random


class Scraper:
    """Scraper class for performing common actions"""

    playwright = False

    settings = False
    parser = False
    storage = False

    browser = False
    context = False
    page = False

    default_timeout = 100000000

    scroll_settings = {
        'scroll': {
            'delta_y': {
                'random': {
                    'min': 750,
                    'max': 1250
                }
            },
            'interval': {
                'random': {
                    'min': 1,
                    'max': 3
                }
            }
        }
    }

    viewport_settings = {
        'height': 1080,
        'width': 1920
    }

    processed_responses = []

    def __init__(self, settings, parser):
        self.settings = settings
        self.parser = parser

        self.playwright = sync_playwright().start()

        self.init_browser()
        self.init_context()
        self.init_page()


    def init_browser(self):

        if(self.settings.settings['proxy'] != ''):
            self.browser = self.playwright.chromium.launch(
                headless = False,
                proxy = {
                    'server': self.settings.settings['proxy']
                },
                slow_mo = 1000
            )
        else:
            self.browser = self.playwright.chromium.launch(
                headless = False,
                slow_mo = 1000
            )

    def init_context(self):
        self.context = self.browser.new_context(
            viewport = {
                "width": self.viewport_settings['width'],
                "height": self.viewport_settings['height']
            },
            storage_state = self.settings.session['storage']
        )


    def init_page(self):
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.default_timeout)



    def finish(self):
        self.context.storage_state(path = self.settings.session['storage'])
        self.context.close()
        self.browser.close()

        self.playwright.stop()


    def load_advanced_search(self, adv_search_url):
        self.page.on("request", self.handle_requests)
        self.page.goto(adv_search_url)

        # Checks for login page was opened
        time.sleep(3)
        login_check = self.page.locator("input[autocomplete='username']")

        print(login_check.count())
        if(login_check.count() > 0):
            self.login()

        # Scrolls and waits
        while(self.parser.added_tweets < self.settings.settings['limit_posts']):
            self.page.mouse.wheel(0, self.random_scroll_delta_y())
            time.sleep(self.random_scroll_interval())
        self.finish()


    def login(self):

        if(not self.page.url.find('login')):
            self.page.goto(self.settings.urls['login'])
            time.sleep(3)

        login_input = self.page.locator("input[autocomplete='username']")
        login_input.fill(self.settings.credentials['login'])

        self.page.get_by_role("button", name="Next").click()

        self.context.storage_state(path = self.settings.session['storage'])

        self.page.locator("input").fill("teiko89")
        self.page.get_by_role("button", name="Next").click()

        password_input = self.page.locator("input[name='password']")
        password_input.fill(self.settings.credentials['password'])

        button_input = self.page.get_by_test_id("LoginForm_Login_Button")
        button_input.click()

        self.context.storage_state(path = self.settings.session['storage'])
        time.sleep(10)


    def handle_requests(self, request):

        if(request.url.find('SearchTimeline') != -1):
            print("New tweets were loaded (API call)")
            response = request.response()
            body = response.json()
            self.parser.parse(body)
            self.processed_responses.append(response)

    def random_scroll_delta_y(self):
        return random.randint(self.scroll_settings['scroll']['delta_y']['random']['min'], self.scroll_settings['scroll']['delta_y']['random']['max'])


    def random_scroll_interval(self):
        return random.randint(self.scroll_settings['scroll']['interval']['random']['min'], self.scroll_settings['scroll']['interval']['random']['max'])