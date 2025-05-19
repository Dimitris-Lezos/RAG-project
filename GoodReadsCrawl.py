import logging
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
import json


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[], books_file="books_file", book_urls_file="book_urls_file"):
        self.visited_book_urls = []
        self.book_urls_to_visit = urls
        self.books_file = open(books_file, "a")
        try:
            file = open(book_urls_file, "r")
            self.visited_book_urls = [line.strip() for line in file.readlines()]
            file.close()
        except Exception:
            pass
        self.book_urls_file = open(book_urls_file, "a")
        self.visited_reviewer_urls = []
        self.reviewer_urls_to_visit = []
        self.driver = webdriver.Firefox()
        self.i = 0

    def __del__(self):
        self.books_file.close()
        self.book_urls_file.close()
        self.driver.close()

    def login(self, username, password):
        self.download_url('https://www.goodreads.com')
        self.driver.find_element(By.LINK_TEXT, "Sign In").click()
        time.sleep(0.1)
        try:
            login_url = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Sign in with email").get_attribute("href")
            self.driver.get(login_url)
        except Exception as e:
            print(e)
        time.sleep(0.1)
        self.driver.find_element(By.ID, "ap_email").send_keys(username)
        self.driver.find_element(By.ID, "ap_password").send_keys(password)
        time.sleep(2)
        self.driver.find_element(By.ID, "signInSubmit").submit()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='Dimitris Lezos']"))
        )

    def download_url(self, url):
        self.driver.get(url)
        time.sleep(2)

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawlBookURL(self, url):
        self.download_url(url)
        book = self.parseBookPage(self.driver)
        book['url'] = url
        if "English" == book['language']:
            self.books_file.write(json.dumps(book, indent=4))
            self.books_file.write(",\n")
        else:
            print("Not English book ", url)
        self.pushReviewers(book)

    def crawlReviewerURL(self, url):
        self.download_url(url)
        book_urls = self.parseReviewerPage(self.driver)
        self.pushBooks(book_urls)

    # Add the reviewers in the list to access
    def pushReviewers(self, book):
        reviews = book['reviews']
        for review in reviews:
            if review['reviewer_url'] not in self.visited_reviewer_urls and review['reviewer_url'] not in self.reviewer_urls_to_visit:
                self.reviewer_urls_to_visit.append(review['reviewer_url'])

    def pushBooks(self, book_urls: []):
        for book_url in book_urls:
            self.pushBook(book_url)

    def pushBook(self, book_url):
        if book_url not in self.visited_book_urls and book_url not in self.book_urls_to_visit:
            self.book_urls_to_visit.append(book_url)

    def parseReviewerPage(self, driver: webdriver):
        book_urls = []
        try:
            driver.find_element(By.LINK_TEXT, "More…").click()
            time.sleep(1)
            Select(driver.find_element(By.ID, "per_page")).select_by_value('100')
            time.sleep(0.5)
            # Scroll to the end of the page so that all the books are loaded
            while True:
                # scroll down 1000 pixels
                driver.execute_script('window.scrollBy(0, 1000)')
                # wait for page to load
                time.sleep(0.5)
                # check if at bottom of page
                if driver.execute_script('return window.innerHeight + window.pageYOffset >= document.body.offsetHeight'):
                    break
            # Find a way to run this find:
            a_books = driver.find_element(By.ID, "books").find_elements(By.CSS_SELECTOR, "a[href*='book/show']")
            for a in a_books:
                try:
                    book_urls.append(a.get_attribute("href"))
                except Exception as e:
                    pass
        except Exception as e:
            print(e)
            pass
        finally:
            return book_urls

    def parseBookPage(self, driver: webdriver):
        language = "English"
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Book details and editions']").click()
            time.sleep(0.05)
        except Exception:
            pass
        try:
            if "English" not in driver.find_element(By.CSS_SELECTOR, "div[class='EditionDetails']").text:
                language = ""
        except Exception:
            pass
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='bookTitle']").text
        except Exception as e:
            title = ""
        try:
            description = driver.find_element(By.CSS_SELECTOR, "div[data-testid='description']").find_element(By.CSS_SELECTOR, "span[class='Formatted']").text
        except Exception as e:
            description = ""
        try:
            genres = []
            all_a = driver.find_element(By.CSS_SELECTOR, "div[data-testid='genresList']").find_elements(By.CSS_SELECTOR, "a")
            for a in all_a:
                try:
                    genres.append(a.text)
                except Exception:
                    pass
        except Exception as e:
            genres = []
        try:
            author = driver.find_element(By.CSS_SELECTOR, "span[data-testid='name']").text
        except Exception as e:
            author = ""
        try:
            author_bio = driver.find_element(By.CSS_SELECTOR, "div[class='PageSection']").find_element(By.CSS_SELECTOR, "div[class='DetailsLayoutRightParagraph']").text
        except Exception as e:
            author_bio = ""
        try:
            reviews = []
            # Get the reviews in the initial page
            self.parseReviewCards(reviews, driver)
            print("parse review cards returned: ", len(reviews))
            # Press the button for more reviews
            more_button = driver.find_element(By.LINK_TEXT, "More reviews and ratings")
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                more_button.click()
            except Exception:
                time.sleep(1)
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                more_button.click()
            # Get the reviews in the new page
            time.sleep(1)
            self.parseReviewCards(reviews, driver)
            print("parse more review cards returned: ", len(reviews))
        except Exception as e:
            print(e)
            pass
        book = {
            'title': title,
            'language': language,
            'description': description,
            'genres': genres,
            'author': {
                'name': author,
                'bio': author_bio
            },
            'reviews': reviews
        }
        return book

    def parseReviewCards(self, reviews: [], driver: webdriver):
        review_cards = driver.find_elements(By.CSS_SELECTOR, "article[class='ReviewCard']")
        print("Review Cards found: ", len(review_cards))
        for review_card in review_cards:
            try:
                review = {
                    'reviewer': review_card.find_element(By.CSS_SELECTOR, "section[class='ReviewerProfile__info']").find_element(By.CSS_SELECTOR, "div[data-testid='name']").text,
                    'content': review_card.find_element(By.CSS_SELECTOR, "section[class='ReviewText__content']").text,
                    'rating': review_card.find_element(By.CSS_SELECTOR, "span[class='RatingStars RatingStars__small']").get_attribute("aria-label"),
                    'date': review_card.find_element(By.CSS_SELECTOR, "section[class='ReviewCard__row']").text,
                    'reviewer_url': review_card.find_element(By.CSS_SELECTOR, "section[class='ReviewerProfile__info']").find_element(By.CSS_SELECTOR, "div[data-testid='name']").find_element(By.TAG_NAME, "a").get_attribute("href")
                }
                reviews.append(review)
            except Exception:
                pass

    def run(self):
        self.books_file.write("[\n")
        while self.book_urls_to_visit or self.reviewer_urls_to_visit:
            if self.book_urls_to_visit:
                url = self.book_urls_to_visit.pop(0)
                self.i += 1
                logging.info(f'Crawling {self.i}: {url}')
                try:
                    self.crawlBookURL(url)
                except Exception:
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    self.visited_book_urls.append(url)
                    self.book_urls_file.write(url+"\n")
            elif self.reviewer_urls_to_visit:
                url = self.reviewer_urls_to_visit.pop(0)
                logging.info(f'Crawling: {url}')
                try:
                    self.crawlReviewerURL(url)
                except Exception:
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    self.visited_reviewer_urls.append(url)
        self.books_file.write("\n{}\n]")

if __name__ == '__main__':
    # Initiate the crawler and selenium
    crawler = Crawler(
        # Use this as the initial URL
        urls=['https://www.goodreads.com/book/show/135737825-the-buried'],
        # The output file
        books_file="books_file_6")
    try:
        # Login at www.goodreads.com
        crawler.login("d.lezos@acg.edu", "FxeB+/p5_L,sR%2")
        # Start Crawling
        crawler.run()
    except Exception as e:
        print(e)
    finally:
        del crawler
