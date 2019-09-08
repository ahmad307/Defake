from django.shortcuts import render
from django.http import JsonResponse
from analysis import helper


def index(request):
    return render(request, 'index.html')


def get_analysis(request):
    response = {}
    url = request.GET['url']

    page = helper.get_html(url)
    article_content = helper.get_article_content(page)
    sentiment = helper.get_analysis(article_content)

    score = sentiment.document_sentiment.magnitude * sentiment.document_sentiment.score
    response['score'] = score

    hot_phrases = helper.get_hot_phrases(sentiment)
    response['hot_phrases'] = hot_phrases

    references = helper.get_references(page)
    trusted_references = helper.evaluate_references(references)
    response['trusted_references'] = trusted_references
    response['total_references'] = len(references)

    return JsonResponse(response)
