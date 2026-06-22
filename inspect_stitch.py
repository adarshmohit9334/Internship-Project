from pathlib import Path
from bs4 import BeautifulSoup

html_path = Path(r'C:\Users\Skand\AppData\Roaming\Code\User\workspaceStorage\424bfea913667d1e835c625aeff9e95c\GitHub.copilot-chat\chat-session-resources\2a3a4c2c-ce5f-4620-afec-1f2ce775edd9\call_iQ3of9kQ6vwbiWdhSoYYgzwA__vscode-1782121067124\content.txt')
html = html_path.read_text(encoding='utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

print('TITLE:', soup.title.text if soup.title else 'No title')

body = soup.body
if body:
    print('\n=== BODY PREVIEW ===')
    print(body.prettify()[:12000])
else:
    print('No body found')
