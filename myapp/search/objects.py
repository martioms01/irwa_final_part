import json


class Document:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, likes, retweets, url, hashtags, user, replycount):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.likes = likes
        self.retweets = retweets
        self.url = url
        self.hashtags = hashtags
        self.user = user
        self.replycount = replycount

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        try:
            json_data = self.to_json()
            return json.dumps(json_data)
        except Exception as e:
            return f"Error during serialization: {str(e)}"
        
    def get_content(self):
        return self.description


class StatsDocument:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, url, count):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.count = count

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class ResultItem:
    def __init__(self, id, title, description, doc_date, url, tweeturl, ranking):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.tweeturl = tweeturl
        self.ranking = ranking


class User:
    def __init__(self, display_name, username, profile_picture):
        self.display_name = display_name
        self.username = username
        self.profile_picture = profile_picture

    @classmethod
    def dict_user(cls, user_dict):
        """Create a User instance from a user dictionary."""
        return cls(
            display_name=user_dict.get('displayname', ''),
            username=user_dict.get('username', ''),
            profile_picture=user_dict.get('profileImageUrl', '')
        )
