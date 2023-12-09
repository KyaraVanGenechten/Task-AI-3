# Importing libraries
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# Functions to scrape the images -> same as in notebook
# Function to create a folder if it doesn't exist
def create_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to save image
def save_image(url, directory, count):
    try:
        response = requests.get(url, stream=True)
        with open(f"{directory}/image_{count}.jpg", 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
    except Exception as e:
        print(f"Failed to save image {url}: {str(e)}")

# Function to scrape images
def scrape_images(keyword, directory, num_images):
    create_folder(directory)
    encoded_query = quote_plus(keyword)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    num_pages = num_images // 100
    count = 0
    for page in range(num_pages):
        url = f"https://www.google.com/search?q={encoded_query}&tbm=isch&start={page*20}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        for img_tag in soup.find_all('img'):
            image_url = img_tag.get('src')
            if image_url and image_url.startswith('http'):
                save_image(image_url, directory, count)
                count += 1
                if count >= num_images:

                    break
# Streamlit app
st.title("Image Classification")

# Button to start scraping images
if st.button('Start Image Scraping'):
    categories = ['dancing', 'yoga', 'swimming', 'running', 'cycling']
    num_images_per_category = 5000
    
    # Add a progress bar
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    for i, category in enumerate(categories, start=1):
        progress_text.text(f"Scraping images for {category}...")
        
        scrape_images(category, f"images/{category}", num_images_per_category)
        
        # Update progress bar
        progress_percent = i / len(categories)
        progress_bar.progress(progress_percent)
    
    progress_text.text("Image scraping process completed!")