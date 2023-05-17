from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        path, _, query_string = self.path.partition('?')
        params = urllib.parse.parse_qs(query_string)
        word = params.get('word', [''])[0]  # Use the 'word' parameter value if it exists, or '' if it doesn't

        if not word:
            # Send an error message if the 'word' parameter is missing
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: Missing "word" parameter. Please provide a word to search for!'.encode('utf-8'))
            return

        # Fetch data from the PIV
        response = requests.get(f'https://vortaro.net/py/serchi.py?simpla=1&s={word}')
        data = response.text

        # Remove HTML tags using BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')
        text = soup.get_text()

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
