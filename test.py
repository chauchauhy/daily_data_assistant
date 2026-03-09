import json
import requests
# newsapi = NewsApiClient(api_key="17d4339a28be4b81a3fb7016af3359fd")

# top_headlines = newsapi.get_everything(q="AI", page_size=10, sort_by="publishedAt", language="en")

url = ('https://newsapi.org/v2/everything?'
       'q=AI&'
       'sortBy=publishedAt&'
       'language=en&'
       'apiKey=17d4339a28be4b81a3fb7016af3359fd')

response = requests.get(url)

result = response.json()


# print(top_headlines)
# print(f"Total results: {result['totalResults']}\n")
articles = result.get('articles', [])
for article in articles[:10]:
    print(f"Source: {article['source']['name']}")
    print(f"Title: {article['title']}")
    print(f"Description: {article['description']}")
    print(f"URL: {article['url']}")
    print(f"Published At: {article['publishedAt']}\n")
# result = []
# for article in top_headlines['articles'][:10]:
#     sub_result = {
#         "source": article['source']['name'],
#         "title": article['title'],
#         "description": article['description'],
#         "url": article['url'],
#         "publishedAt": article['publishedAt']
#     }
#     if len(article['description']) > 100:
#         result.append(sub_result)
    
    
# print(json.dumps(result, indent=2))
# print(len(json.dumps(result, indent=2)))
