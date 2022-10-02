import requests

class TelegramAlert:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = str(chat_id)

    def text(self, text):
        url_path = self.__url_path(self.token)
        parameters = { "chat_id" : self.chat_id, "text" : text }
        r = requests.get(url_path, params=parameters)
        return r

    def __url_path(self, token):
        url = "https://api.telegram.org"
        path = "/bot{0}/sendMessage".format(token)
        url_path = url + path
        return url_path
