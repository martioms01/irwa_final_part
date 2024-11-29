import pandas as pd
import re
import json
from myapp.core.utils import load_json_file
from myapp.search.objects import Document, User

_corpus = {}


def load_corpus(path) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    tweets = load_tweets_from_json(path)

    if not tweets:
        print("No tweets found!")
        return []
     # Transform tweet dictionary to a DataFrame
    df = pd.DataFrame(tweets)

    # Clean and process hashtags and URLs
    _clean_hashtags_and_urls(df)
    
    corpus = df.rename(
         columns={"id": "Id", "content": "Tweet", "user": "Username", "date": "Date",
                 "likeCount": "Likes",
                 "retweetCount": "Retweets", "lang": "Language", "url": "Url", "hashtags": "Hashtags"})
    
    print(corpus.columns)
    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Likes", "Retweets", "Language", "Url", "Hashtags", "replyCount"]
    corpus = corpus[filter_columns]
    

    # Apply the row-to-document transformation
    corpus.apply(_row_to_doc_dict, axis=1)

    return _corpus

def load_tweets_from_json(file_path):
    """Function to load the tweets from the json file into a dictionary of key: tweet id, value: tweet object

    Args:
        file_path (string): Path to the json file

    Returns:
        Dict[int, Tweet]: Dictionary mapping tweet ids to tweet objects. It allows fast retrieval of tweets when indexing by id.
    """
    tweets = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                tweet = json.loads(line.strip())
                tweets.append(tweet)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line} - {str(e)}")
    return tweets


def _clean_hashtags_and_urls(df):
    df["hashtags"] = df["content"].apply(_build_tags)
    #df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    #df['url'] = df['url'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')

    # df["Url"] = "TODO: get url from json"


def _row_to_doc_dict(row: pd.Series):

    user_info = row['Username']  # This is the dictionary with user data

    # Create a User instance using the relevant fields from the user_info dictionary
    user = User(
        display_name=user_info.get('displayname', ''),  # Safely access 'displayname'
        username=user_info.get('username', ''),        # Safely access 'username'
        profile_picture=user_info.get('profileImageUrl', '')  # Safely access 'profileImageUrl'
    )
    
    title = row['Tweet'][:100] if row['Tweet'] else "No title"
    _corpus[row['Id']] = Document(row['Id'], title, row['Tweet'], row['Date'], row['Likes'],
                                  row['Retweets'], row["Url"], row["Hashtags"], user, row["replyCount"])
    

def _build_tags(row):
    tags = []
    tags = re.findall(r"#\w+", row)
    return tags


# def _load_corpus_as_dataframe(path):
#     """
#     Load documents corpus from file in 'path'
#     :return:
#     """
#     json_data = load_json_file(path)
#     tweets_df = pd.DataFrame([json_data])

#     _clean_hashtags_and_urls(tweets_df)
#     # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
#     corpus = tweets_df.rename(
#         columns={"id": "Id", "content": "Tweet", "user": "Username", "date": "Date",
#                  "likeCount": "Likes",
#                  "retweetCount": "Retweets", "lang": "Language", "url": "Url", "hashtags": "Hashtags"})

#     # select only interesting columns
#     filter_columns = ["Id", "Tweet", "Username", "Date", "Likes", "Retweets", "Language", "Url", "Hashtags"]
#     corpus = corpus[filter_columns]
#     return corpus

# """
# def _load_tweets_as_dataframe(json_data):

#     data = pd.DataFrame(json_data).transpose()
#     # parse entities as new columns
#     data = pd.concat([data.drop(['entities'], axis=1), data['entities'].apply(pd.Series)], axis=1)
#     # parse user data as new columns and rename some columns to prevent duplicate column names
#     data = pd.concat([data.drop(['user'], axis=1), data['user'].apply(pd.Series).rename(
#         columns={"created_at": "user_created_at", "id": "user_id", "id_str": "user_id_str", "lang": "user_lang"})],
#                      axis=1)
#     return data
# """

# def _build_url(row):
#     url = ""
#     try:
#         url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
#     except:
#         try:
#             url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
#         except:
#             url = ""
#     return url


