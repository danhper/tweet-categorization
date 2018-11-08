import re
import json
import MeCab
from requests_oauthlib import OAuth1Session
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

CK = os.environ.get('TWITTER_CONSUMER_KEY')
CS = os.environ.get('TWITTER_CONSUMER_SECRET')
AT = os.environ.get('TWITTER_ACCESS_TOKEN')
AS = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

API_URL = "https://api.twitter.com/1.1/search/tweets.json?tweet_mode=extended"
KEYWORD = "芸能 OR アニメ OR 漫画 OR TV OR ゲーム"  # entertainment
CLASS_LABEL = "__label__1"


# KEYWORD = "コスメ OR 美容 OR 化粧品 OR ネイル OR 健康" # beauty
# CLASS_LABEL = "__label__2"
# KEYWORD = "ペット OR 散歩 OR 運動 OR 寝る OR 食べる"  # lifestyle
# CLASS_LABEL = "__label__3"


def main():
    tweets = get_tweet()
    surfaces = get_surfaces(tweets)
    write_txt(surfaces)


def get_tweet():
    twitter = OAuth1Session(CK, CS, AT, AS)
    results = []

    def search_tweet(params, num=0):
        if num == 30:
            return results
        req = twitter.get(API_URL, params=params)
        if req.status_code == 200:
            tweets = json.loads(req.text)
            for tweet in tweets['statuses']:
                results.append(tweet['full_text'])
            max_id = tweets['statuses'][-1]['id_str']
            return search_tweet({'q': KEYWORD, 'count': 100, 'max_id': max_id}, num + 1)
        else:
            print("Error: %d" % req.status_code)
            return results

    return search_tweet({'q': KEYWORD, 'count': 100})


def get_surfaces(contents):
    """
    文書を分かち書きし単語単位に分割
    """
    results = []
    for row in contents:
        content = format_text(row)
        tagger = MeCab.Tagger('')
        tagger.parse('')
        surf = []
        node = tagger.parseToNode(content)
        while node:
            surf.append(node.surface)
            node = node.next
        results.append(surf)
    return results


def write_txt(contents):
    """
    create text for evaluation model
    """
    try:
        if len(contents) > 0:
            file_name = CLASS_LABEL + ".txt"
            label_text = CLASS_LABEL + ", "

            f = open(file_name, 'a')
            for row in contents:
                # 空行区切りの文字列に変換
                space_tokens = " ".join(row)
                result = label_text + space_tokens + "\n"
                # 書き込み
                f.write(result)
            f.close()

        print(str(len(contents)) + "line done")

    except Exception as e:
        print("fail to write text file")
        print(e)


def format_text(text):
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub(r'@[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub(r'&[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub(';', "", text)
    text = re.sub('RT', "", text)
    text = re.sub('\n', " ", text)
    return text


if __name__ == '__main__':
    main()
