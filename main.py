# Importing libraries
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from PIL import Image

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

# More information about the task and my categories
st.write("This Streamlit app is about image classification")
st.write("The subject of the photos I chose is sports. I chose 5 different categories, such as swimming, cycling, dancing, yoga and running.")

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
    
    progress_text.text("Image scraping completed!")

# Performing a small EDA
if st.button('Perform Small EDA'):

    # folder where images are stored
    folder = 'images'

    # List all subfolders
    categories = os.listdir(folder)

    st.write("Number of images in each category:")
    # Display number of images in each category
    for category in categories:
        path = os.path.join(folder, category)
        if os.path.isdir(path):
            num_images = len(os.listdir(path))
            st.write(f"{category}: {num_images} images")

    # 2.2 Performing a small EDA
    # Function called display_images to display 2 images from each category
    # This function has 2 parameters: category, number
    def show_images(category_name, number=2):
        st.subheader(f"Images for {category_name}")
        # path of the folders
        path = os.path.join(folder, category_name)
        image_files = os.listdir(path)
        
        # Check if there are at least 2 images available in the category
        num_images_available = len(image_files)
        if num_images_available < 2:
            st.write("You need to click on the button to start image scrappping and then you can perform a small EDA")
            return

        # For 2 images
        for i in range(number):
            # Path of the image
            img_path = os.path.join(path, image_files[i])
            # Show the image with no axis and set the pictures next to each other
            img = Image.open(img_path)
            st.image(img, caption=f"Image {i+1}", use_column_width=True)


    # Display 2 images from each class and call the function show_images
    for category in categories:
        show_images(category)
