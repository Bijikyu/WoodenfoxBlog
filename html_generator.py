```python
# This script provides functionality to read markdown blog posts, fetch and update images, parse dates, 
# convert markdown to HTML, and generate a single HTML file with all posts formatted using Bootstrap.

import requests  # Import the requests library to make HTTP requests
import os  # Import the os library to interact with the operating system
import yaml  # Import the yaml library to parse YAML content
import markdown2  # Import the markdown2 library to convert markdown text to HTML
from dateutil import parser  # Import the parser from dateutil to parse date strings
from datetime import datetime  # Import the datetime class from the datetime module

# Define a function to fetch an image from a URL and save it to a local directory
def fetch_image(url, save_path):
  response = requests.get(url, stream=True)  # Send a GET request to the URL and enable streaming of the response
  response.raise_for_status()  # Raise an HTTPError if the response was an HTTP error
  with open(save_path, 'wb') as file:  # Open the save_path in binary write mode as file
    for chunk in response.iter_content(chunk_size=8192):  # Iterate over the response in chunks of 8192 bytes
      file.write(chunk)  # Write the chunk to the file
  return save_path  # Return the path where the image was saved

# Define a function to handle the post image and return updated YAML and markdown content
def handle_post_image(yaml_content, markdown_content, image_dir):
  if not os.path.exists(image_dir):  # Check if the image directory does not exist
    os.makedirs(image_dir)  # Create the image directory

  image_url = yaml_content.get('image', None)  # Get the image URL from the YAML content
  if image_url and not image_url.startswith('/images/'):  # Check if the image URL exists and does not start with '/images/'
    image_filename = os.path.basename(image_url)  # Extract the filename from the image URL
    local_image_path = os.path.join(image_dir, image_filename)  # Construct the local image path
    fetch_image(image_url, local_image_path)  # Fetch and save the image locally

    markdown_content = markdown_content.replace(image_url, '/' + local_image_path)  # Replace the image URL in the markdown content

    yaml_content['image'] = '/' + local_image_path  # Update the 'image' attribute in the YAML content

  return yaml_content, markdown_content  # Return the updated YAML content and markdown content

# Define a function to parse a date string into a datetime object with flexible format handling
def parse_date(date_str):
  if isinstance(date_str, datetime):  # Check if date_str is already a datetime object
    return date_str  # Return the datetime object directly
  elif not date_str:  # Check if date_str is None or empty
    return None  # Return None
  try:
    return parser.parse(date_str)  # Attempt to parse the date string
  except (ValueError, TypeError):  # Catch ValueError or TypeError exceptions
    return None  # Return None if parsing fails

# Define a function to read markdown files from a specified folder and parse YAML and Markdown
def read_markdown_files(folder_path):
  posts = []  # Initialize an empty list to store posts
  image_dir = "images"  # Define the image directory
  if not os.path.exists(image_dir):  # Check if the image directory does not exist
    os.makedirs(image_dir)  # Create the image directory

  for filename in os.listdir(folder_path):  # Iterate over files in the folder_path
    if filename.endswith(".md"):  # Check if the file has a .md extension
      file_path = os.path.join(folder_path, filename)  # Construct the full file path
      with open(file_path, 'r', encoding='utf-8') as file:  # Open the file in read mode with UTF-8 encoding
        content = file.read()  # Read the content of the file

      parts = content.split('---', 2)  # Split the content into parts using '---' as the delimiter
      yaml_content = yaml.safe_load(parts[1]) if len(parts) > 1 else {}  # Parse the YAML content
      markdown_content = parts[2] if len(parts) > 2 else parts[0]  # Get the markdown content

      original_image_url = yaml_content.get('image', None)  # Get the original image URL from the YAML content
      yaml_content, markdown_content = handle_post_image(yaml_content, markdown_content, image_dir)  # Process the image and update content

      new_image_url = yaml_content.get('image', None)  # Get the new image URL from the updated YAML content
      if new_image_url and new_image_url != original_image_url:  # Check if the image URL was updated
        relative_image_path = os.path.join('/images', os.path.basename(new_image_url))  # Construct the relative image path
        yaml_content['image'] = relative_image_path  # Update the 'image' attribute in the YAML content
        updated_content = '---\n' + yaml.dump(yaml_content) + '---\n' + markdown_content  # Construct the updated content with YAML and markdown
        with open(file_path, 'w', encoding='utf-8') as file:  # Open the file in write mode with UTF-8 encoding
          file.write(updated_content)  # Write the updated content to the file

      date = parse_date(yaml_content.get('date', ''))  # Parse the date from the YAML content
      posts.append({  # Append the post information to the posts list
          'metadata': yaml_content,
          'content': markdown_content,
          'date': date
      })

  posts.sort(key=lambda x: x['date'] if x['date'] is not None else datetime.min, reverse=True)  # Sort posts by date, most recent first
  return posts  # Return the list of posts

# Define a function to convert markdown text to HTML
def convert_markdown_to_html(markdown_text):
  return markdown2.markdown(markdown_text)  # Convert the markdown text to HTML and return it

# Define a function to generate a single HTML file from the list of posts with Bootstrap
def generate_html(posts, header_path, footer_path):
  with open(header_path, 'r', encoding='utf-8') as file:  # Open the header file in read mode with UTF-8 encoding
    header = file.read()  # Read the header content

  with open(footer_path, 'r', encoding='utf-8') as file:  # Open the footer file in read mode with UTF-8 encoding
    footer = file.read()  # Read the footer content

  body_content = "<div class='grid'>"  # Start the body content with a div element for the grid
  for post in posts:  # Iterate over each post in the posts list
    html_content = convert_markdown_to_html(post['content'])  # Convert the markdown content to HTML
    title = post['metadata'].get('title', 'No Title')  # Get the title from the post metadata
    date_str = post['date'].strftime('%B %d, %Y at %H:%M') if post['date'] else 'Unknown Date'  # Format the date string

    image_html = f"<img src='{post['metadata'].get('image', '')}' class='card-img-top' alt='{title}'>" if post['metadata'].get('image') else ''  # Construct the image HTML if an image is present

    body_content += f'''
            <div class='grid-item card my-3'>
                {image_html}
                <div class='card-body'>
                    <h2 class='card-title'>{title}</h2>
                    <p class='card-text'><small class='text-muted'>{date_str}</small></p>
                    {html_content}
                </div>
            </div>
        '''  # Append the post HTML to the body content
  body_content += "</div>"  # Close the grid div element
  return header + body_content + footer  # Return the complete HTML content by concatenating the header, body, and footer