from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.oauth2 import service_account

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import os


def remove_script_tag(soup):
    for tag in soup('script'):
        tag.decompose()


def remove_attributes(soup):
    for tag in soup.recursiveChildGenerator():
        if hasattr(tag, 'attrs'):
            tag.attrs = {}


def get_article_content(soup):
    """Takes cleaned soup object and returns p tags as one object."""
    paragraphs = soup('p')
    article = ''
    for paragraph in paragraphs:
        if len(paragraph.contents):
            article += str(paragraph.contents[0])
            article += '\n'
    return article


def get_html(url):
    page_content = requests.get(url).content
    soup = BeautifulSoup(page_content, 'html.parser')('body')[0]
    return soup


def clean_soup(soup):
    """Cleans soup object from any tags but body and removes all tag attributes."""
    remove_attributes(soup)
    remove_script_tag(soup)


def get_reference_name(ref):
    """Extracts website name from the href of a given a tag."""
    url = ref.attrs['href']
    website_name = urlparse(url).netloc
    website_name = str(website_name).replace('www.', '')
    return website_name


def get_references(soup):
    """Receives plain soup object and extracts references to other websites."""
    total_references = []
    paragraphs = soup('p')
    for paragraph in paragraphs:
        references = paragraph('a')
        for ref in references:
            total_references.append(get_reference_name(ref))
    return total_references


def get_analysis(article):
    "Evaluates a document sentiment."
    credentials = service_account.Credentials.from_service_account_file("D:\Projects\Defake - tests\creds.json")
    client = language.LanguageServiceClient(credentials=credentials)

    # The text to analyze
    #text = 'Hi'
    document = types.Document(content=article, type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document)

    #print(sentiment)
    #return sentiment.magnitude * sentiment.score
    return sentiment


def get_hot_phrases(sentiment_analysis):
    hot_sentences = []
    for sentence in sentiment_analysis.sentences:
        if (sentence.sentiment.magnitude * sentence.sentiment.score > 0.5 or
            sentence.sentiment.magnitude * sentence.sentiment.score < -0.5):
            hot_sentences.append(sentence.text.content)
    return hot_sentences


def evaluate_references(references):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'websites.txt')
    trusted_websites = open(file_path, 'r').read().replace('\n', '').split(',')

    trusted = 0
    for reference in references:
        if reference in trusted_websites:
            trusted += 1
    return trusted
