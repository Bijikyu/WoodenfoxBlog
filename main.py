from flask import Flask, send_from_directory
from html_generator import read_markdown_files, generate_html
import os

app = Flask(__name__, static_folder='_site', static_url_path='')


def main():
  folder_path = "posts"
  template_path = "templates"

  header_path = os.path.join(template_path, 'header.html')
  footer_path = os.path.join(template_path, 'footer.html')

  posts = read_markdown_files(folder_path)
  html = generate_html(posts, header_path, footer_path)

  if not os.path.exists("_site"):
    os.makedirs("_site")

  with open("_site/index.html", "w", encoding='utf-8') as file:
    file.write(html)
  print("HTML file generated successfully.")


@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
  main()
  app.run(host='0.0.0.0', port=8080)
