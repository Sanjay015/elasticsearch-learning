import json
import logging
import os
from time import sleep

import requests
from bs4 import BeautifulSoup



logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
    format='%(asctime)s - %(levelname)s - %(process)s - %(message)s')


HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)'
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/66.0.3359.181 Safari/537.36'),
    'Pragma': 'no-cache',
}

RECIPE_SITE_LINK = os.environ.get(
    'RECIPE_SITE_LINK', 'https://www.allrecipes.com/recipes/96/salad/')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

RECIPE_LINKS_FILE = os.path.join(
    BASE_PATH,
    os.environ.get('RECIPE_LINKS_FILE', 'data/recipe-urls.txt'))

RECIPE_DATA_FILE = os.path.join(
    BASE_PATH,
    os.environ.get('RECIPE_DATA_FILE', 'data/recipe-data.json'))


def fetch_recipe_details(url):
    title = '-'
    submit_by = '-'
    description = '-'
    calories = 0
    ingredients = []
    rec = {}

    try:
        recipe = requests.get(url, headers=HEADERS)

        if recipe.status_code == 200:
            html = recipe.text
            soup = BeautifulSoup(html, 'lxml')
            # title
            title_section = soup.select('.recipe-main-header .heading-content')
            # submitter
            submitter_section = soup.select('.author-name')
            # description
            description_section = soup.select('.recipe-summary')
            # ingredients
            ingredients_section = soup.select('.ingredients-item')

            # calories
            nutrition_section = soup.select('.recipe-nutrition')
            if nutrition_section:
                calories_section = nutrition_section[0].select('.nutrition-top')
                if calories_section:
                    calories = calories_section[0].text.strip().split('\n')[-1]
                    calories = float(calories.split(':')[-1].strip())

            if ingredients_section:
                for ingredient in ingredients_section:
                    ingredients.append({'step': ingredient.text.strip()})

            if description_section:
                description = description_section[0].text.strip().replace('"', '')

            if submitter_section:
                submit_by = submitter_section[0].text.strip()

            if title_section:
                title = title_section[0].text

            rec = {'title': title,
                   'submitter': submit_by,
                   'description': description,
                   'calories': calories,
                   'ingredients': ingredients,
                   'url': url,}

    except Exception as ex:
        logging.error('Exception while parsing url %s. %s', url, str(ex))
    finally:
        return json.dumps(rec)


def load_recipe_links():
    """Load recipe URLs."""
    os.makedirs(os.path.dirname(RECIPE_LINKS_FILE), exist_ok=True)
    if not os.path.exists(RECIPE_LINKS_FILE):
        logging.info(('Recipe URL file(%s) does not exists.'
                      'Loading recipe URLs from recipe site: %s'),
                      RECIPE_LINKS_FILE, RECIPE_SITE_LINK)
        links = []
        recipe_links = requests.get(RECIPE_SITE_LINK, headers=HEADERS)
        if recipe_links.status_code == 200:
            soup = BeautifulSoup(recipe_links.text, 'lxml')
            urls = soup.select('.category-page-item-content__title')
            with open(RECIPE_LINKS_FILE, 'w') as recipe_urls:
                for url in urls:
                    links.append(url['href'])
                    recipe_urls.write('{}\n'.format(url['href']))
        else:
            logging.error(
                'Unable to connect to recipe site: %s. Respoonse code: %s',
                RECIPE_SITE_LINK, recipe_links.status_code)
        return links

    with open(RECIPE_LINKS_FILE) as recipe_urls:
        logging.info('Loading recipe urls from: %s', RECIPE_LINKS_FILE)
        return [recipe_url.strip() for recipe_url in recipe_urls.readlines()]


def write_recipe_data_to_file(data: list):
    """Write salad recipe data to JSON file."""
    os.makedirs(os.path.dirname(RECIPE_DATA_FILE), exist_ok=True)
    with open(RECIPE_DATA_FILE, 'w') as recipe_data:
        json.dump(data, recipe_data)
    logging.info('Successfully loaded all recipe data to: %s', RECIPE_DATA_FILE)


def load_recipe_data():
    """Load data from recipe data json file."""
    logging.info('Loading recipe data from file: %s.', RECIPE_DATA_FILE)

    with open(RECIPE_DATA_FILE) as recipe_data:
        return json.load(recipe_data)


def get_recipes():
    links = load_recipe_links()
    results = []
    if not os.path.exists(RECIPE_DATA_FILE):
        logging.info(
            ('Recipe data does not exists at: %s. '
            'Extracting recipe data from URL: %s'),
            RECIPE_DATA_FILE, RECIPE_SITE_LINK)
        for link in links:
            logging.info('Extracting data for url: %s', link)
            sleep(2)
            # Fetch recipe details
            result = fetch_recipe_details(link)
            results.append(result)
            logging.info('Fetched result for: %s', link)
        logging.info('Storing data to file: %s', RECIPE_DATA_FILE)
        # Write recipe data to file
        write_recipe_data_to_file(results)
        return results

    return load_recipe_data()
