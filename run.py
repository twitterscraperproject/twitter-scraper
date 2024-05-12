from helpers.settings import Settings
from helpers.parser import Parser
from helpers.writers import CSVWriter, GSWriter
from helpers.scraper import Scraper


settings = Settings()
for category, adv_search_url in settings.settings['category_and_adv_search_url'].items():
    print(category)
    if settings.writer['type'] == 'csv':
        writer = CSVWriter(settings.writer['path'], category)
    else:
        writer = GSWriter(settings.writer['spreadsheet_name'], category, settings.writer['sharing_email'])
    parser = Parser(writer, settings)

    # Production run
    scraper = Scraper(settings, parser)
    scraper.load_advanced_search(adv_search_url)