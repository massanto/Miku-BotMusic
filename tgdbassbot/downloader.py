# /usr
import requests
import time
import urllib3

urllib3.disable_warnings()


class SongsDownloader:

    def __init__(self, song_name="Pass", r=requests.Session()):

        self.song_name = song_name
        self.r = r

    def get_songs_list(self, count):

        self.count = count
        headers = {
            'user-agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}

        params = {'search': self.song_name, 'time': time.ctime()}

        self.response = self.r.get(
            "https://vk.music7s.cc/api/search.php?", headers=headers, params=params, verify=False)

        if self.response.status_code == 200:
            try:
                formated_list = []
                urls_list = []
                without_formating = []
                i = 1
                for item in self.response.json()['items']:
                    if i == self.count + 1:
                        i = 1

                    if len(item['title']) > 50 or len(item['artist']) > 50:
                        continue
                    formated_list.append(
                        f"<b>{i}</b>. {item['title']} - {item['artist']} <em>{item['duration']}</em>")
                    urls_list.append(f"{item['url']}")
                    without_formating.append(item)
                    i += 1

                def f(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]

                def u(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]

                def w(A, n=self.count):
                    return [A[i:i + n]
                            for i in range(0, len(A), n)]

                return f(formated_list), u(urls_list), w(without_formating)

            except KeyError:
                return "NoSongs", "NoSongs"
        else:
            return False

    def download_song(self, link):
        self.link = link
        headers = {
            'user-agent':
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
        self.response = self.r.get(
            f"https://vk.music7s.cc{self.link}", headers=headers, verify=False)

        if self.response.status_code == 200:
            return self.response.content

        else:
            return False
