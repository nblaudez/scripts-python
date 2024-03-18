import irc.bot
from youtube_dl import YoutubeDL
import requests
from bs4 import BeautifulSoup

class YouTubeBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        # YouTube API key and IRC server details
        self.api_key = "YOUR GOOGLE API KEY"
        self.server = "labynet.fr"
        self.port = 6667
        self.channel = "#labynet"
        self.nickname = "rosalie"
        self.realname = "rosalie Bot"
        self.username = "rosalie"

        irc.bot.SingleServerIRCBot.__init__(self, [(self.server, self.port)], self.nickname, self.realname)

    def on_welcome(self, connection, event):
        # Join the specified channel upon successfully connecting to the IRC server
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        # Respond to messages posted in the channel starting with !yt
        message = event.arguments[0]
        if message.startswith('!yt'):
            # Extract the query from the message
            query = message.split('!yt')[1].strip()
            # Search YouTube for matching videos based on the query
            video_id, video_title = self.search_youtube(query)
            if video_id:
                # If a matching video is found, construct and send a message with its URL and title
                complete_url = f"https://www.youtube.com/watch?v={video_id.decode('utf-8')}"
                message = f"YouTube: {complete_url}"
                connection.privmsg(self.channel, message)
            else:
                # If no matching video is found, notify the channel
                connection.privmsg(self.channel, "No corresponding video found.")

        # Check for HTTP links in the message
        links = self.extract_http_links(message)
        for link in links:
            title = self.get_page_title(link)
            if title:
                connection.privmsg(self.channel, f"{title}")

    def search_youtube(self, query):
        # Options for youtube_dl to search YouTube
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'extract_flat': True,
            'default_search': 'auto',
            'youtube_include_dash_manifest': False,
            'youtube_api_key': self.api_key
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract information from YouTube based on the query
                info_dict = ydl.extract_info("ytsearch:" + query, download=False)
                if 'entries' in info_dict:
                    # Retrieve the ID and title of the first matching video
                    video_info = info_dict['entries'][0]
                    video_id = video_info['id']
                    video_title = video_info['title']
                    # Encode video ID and title using UTF-8 to handle special characters
                    return video_id.encode('utf-8'), video_title.encode('utf-8')
            except Exception as e:
                # Handle any exceptions that occur during the YouTube search
                print("Error:", e)
                return None, None

    def extract_http_links(self, message):
        # Extract HTTP links from the message
        import re
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)

    def get_page_title(self, link):
        # Retrieve the title of the webpage
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.title.string
        except Exception as e:
            print("Error:", e)
            return None

if __name__ == "__main__":
    # Create an instance of the YouTubeBot and start it
    bot = YouTubeBot()
    bot.start()
