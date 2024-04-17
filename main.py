```python
# This Flask application generates a static HTML file from markdown files and serves it on a web server.

from flask import Flask, send_from_directory  # Import Flask class and send_from_directory function from the flask module.
from html_generator import read_markdown_files, generate_html  # Import custom functions from html_generator module.
import os  # Import os module to interact with the operating system.

app = Flask(__name__, static_folder='', static_url_path='')  # Create a Flask app instance with the current module name and configure static file serving.

# Main function that reads markdown files, generates HTML, and writes it to 'index.html'.
def main():
  folder_path = "posts"  # Define the path to the folder containing markdown files.
  template_path = "templates"  # Define the path to the folder containing HTML templates.

  header_path = os.path.join(template_path, 'header.html')  # Construct the full path to the header template.
  footer_path = os.path.join(template_path, 'footer.html')  # Construct the full path to the footer template.

  posts = read_markdown_files(folder_path)  # Read markdown files from the specified folder and store the content.
  html = generate_html(posts, header_path, footer_path)  # Generate HTML content by combining markdown content with header and footer.

  with open("index.html", "w", encoding='utf-8') as file:  # Open 'index.html' for writing with UTF-8 encoding.
    file.write(html)  # Write the generated HTML content to the file.
  print("HTML file generated successfully.")  # Print a success message to the console.

# Route to serve the generated 'index.html' file at the root URL.
@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'index.html')  # Send 'index.html' from the static folder as a response to the client.

# Entry point of the script that runs the main function and starts the Flask server.
if __name__ == "__main__":
  main()  # Call the main function to generate the HTML file.
  app.run(host='0.0.0.0', port=8080)  # Start the Flask server on host 0.0.0.0 and port 8080.