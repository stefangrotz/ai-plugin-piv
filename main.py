from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        path, _, query_string = self.path.partition('?')
        params = urllib.parse.parse_qs(query_string)
        word = params.get('word', [''])[0]

        if not word:
            # Send an error message if the 'word' parameter is missing
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: Missing "word" parameter. Please provide a word to search for like this: /api/?word=ekzemplo'.encode('utf-8'))
            return

        # Fetch data from the PIV
        response = requests.get(f'https://vortaro.net/py/serchi.py?simpla=1&s={word}')
        data = response.text

        # Remove HTML tags using BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')

        # Remove span elements with class 's'
        for span in soup.find_all('span', {'class': 's'}):
            span.decompose()

        # Select only the main article content
        article = soup.find(id='trovoj')

        if article:
            text = article.get_text()
            # Remove empty lines
            text = "\n".join(line for line in text.splitlines() if line.strip())
        else:
            text = ''

        if not text.strip():
            self.send_response(404)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(('Error: The search did not return a result, most likely the searched word does not exist.').encode('utf-8'))
            return

        # Send the response
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

        return
