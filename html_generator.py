import requests
import os
import yaml
import markdown2
from dateutil import parser
from datetime import datetime


def fetch_image(url, save_path):
  """Fetch image from URL and save to local directory."""
  response = requests.get(url, stream=True)
  response.raise_for_status()
  with open(save_path, 'wb') as file:
    for chunk in response.iter_content(chunk_size=8192):
      file.write(chunk)
  return save_path


def handle_post_image(yaml_content, markdown_content, image_dir):
    """Handle post image and return updated yaml_content and markdown_content."""
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    image_url = yaml_content.get('image', None)
    if image_url and not image_url.startswith('/images/'):
        # Fetch and save the image locally
        image_filename = os.path.basename(image_url)
        local_image_path = os.path.join(image_dir, image_filename)
        fetch_image(image_url, local_image_path)
    
        # Replace the old image URL with the new local path in the Markdown content
        markdown_content = markdown_content.replace(image_url, '/' + local_image_path)
    
        # Update the 'image' attribute in the yaml_content
        yaml_content['image'] = '/' + local_image_path  # Update the image path to local path
    
    return yaml_content, markdown_content



def parse_date(date_str):
  """Parse the date string into a datetime object with flexible format handling."""
  if isinstance(date_str, datetime):
    # If date_str is already a datetime object, return it directly
    return date_str
  elif not date_str:
    # If date_str is None or empty, return None
    return None
  try:
    return parser.parse(date_str)
  except (ValueError, TypeError):
    return None


def read_markdown_files(folder_path):
  """Read markdown files from the specified folder and parse YAML and Markdown, and update them if needed."""
  posts = []
  image_dir = "_site/images"
  if not os.path.exists(image_dir):
      os.makedirs(image_dir)

  for filename in os.listdir(folder_path):
      if filename.endswith(".md"):
          file_path = os.path.join(folder_path, filename)
          with open(file_path, 'r', encoding='utf-8') as file:
              content = file.read()

          parts = content.split('---', 2)
          yaml_content = yaml.safe_load(parts[1]) if len(parts) > 1 else {}
          markdown_content = parts[2] if len(parts) > 2 else parts[0]

          # Process the image and update content
          original_image_url = yaml_content.get('image', None)
          yaml_content, markdown_content = handle_post_image(
              yaml_content, markdown_content, image_dir)

          # Check if the image URL was updated and rewrite file if needed
          new_image_url = yaml_content.get('image', None)
          if new_image_url and new_image_url != original_image_url:
              relative_image_path = os.path.join('/images', os.path.basename(new_image_url))
              yaml_content['image'] = relative_image_path
              updated_content = '---\n' + yaml.dump(yaml_content) + '---\n' + markdown_content
              with open(file_path, 'w', encoding='utf-8') as file:
                  file.write(updated_content)

          date = parse_date(yaml_content.get('date', ''))
          posts.append({
              'metadata': yaml_content,
              'content': markdown_content,
              'date': date
          })

  # Sort posts by date, most recent first
  posts.sort(key=lambda x: x['date'] if x['date'] is not None else datetime.min, reverse=True)
  return posts



def convert_markdown_to_html(markdown_text):
  """Convert markdown text to HTML."""
  return markdown2.markdown(markdown_text)


def generate_html(posts, header_path, footer_path):
    """Generate a single HTML file from the list of posts with Bootstrap."""
    with open(header_path, 'r', encoding='utf-8') as file:
        header = file.read()
  
    with open(footer_path, 'r', encoding='utf-8') as file:
        footer = file.read()
  
    body_content = "<div class='grid'>"
    for post in posts:
        html_content = convert_markdown_to_html(post['content'])
        title = post['metadata'].get('title', 'No Title')
        date_str = post['date'].strftime('%B %d, %Y at %H:%M') if post['date'] else 'Unknown Date'
  
        # Include image if present
        image_html = f"<img src='{post['metadata'].get('image', '')}' class='card-img-top' alt='{title}'>" if post['metadata'].get('image') else ''
  
        body_content += f'''
            <div class='grid-item card my-3'>
                {image_html}
                <div class='card-body'>
                    <h2 class='card-title'>{title}</h2>
                    <p class='card-text'><small class='text-muted'>{date_str}</small></p>
                    {html_content}
                </div>
            </div>
        '''
    body_content += "</div>"
    return header + body_content + footer