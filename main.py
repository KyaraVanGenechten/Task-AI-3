# Importing libraries
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from PIL import Image
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.preprocessing.image import ImageDataGenerator

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
        st.write(f"Failed to save image {url}: {str(e)}")

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
            st.image(img, caption=f"Photo {i+1}")


    # Display 2 images from each class and call the function show_images
    for category in categories:
        show_images(category)

st.write("Train your model")
epochs = st.sidebar.slider("Select the number of epochs", min_value=1, max_value=50, value=20, step=1)
if st.button('Train Model'):
    # Define a slider for selecting the number of epochs
    epochs = st.sidebar.slider("Select the number of epochs", min_value=1, max_value=50, value=20, step=1)

    # Display the selected epochs
    st.write(f"Training will run for {epochs} epochs")

    # 2 Designing a CNN network

    train_val_datagen = ImageDataGenerator(validation_split=0.2,
                                    rescale = 1./255,
                                    shear_range = 0.2,
                                    zoom_range = 0.2,
                                    horizontal_flip = True)

    test_datagen = ImageDataGenerator(rescale = 1./255)

    # 3 sets: training, validation and test set
    # give folder 'images/' , the subset is what is does for example training, the images will be shaped to 64 x 64 pixel. batch_size means that after 32 photos the loss will be calculated for that batch
    # the class_mode is categorical because we have a few categories. 
    training_set = train_val_datagen.flow_from_directory('images/',
                                                    subset='training',
                                                    target_size = (64, 64),
                                                    batch_size = 32,
                                                    class_mode = 'sparse') 

    validation_set = train_val_datagen.flow_from_directory('images/',
                                                    subset='validation',
                                                    target_size = (64, 64),
                                                    batch_size = 32,
                                                    class_mode = 'sparse')

    test_set = test_datagen.flow_from_directory('images/',
                                                target_size = (64, 64),
                                                batch_size = 32,
                                                class_mode = 'sparse')


    # 3 Design a CNN network
    # initialising the CNN
    model = Sequential()

    # 32-> number of filters, 3,3-> size of filter
    # input shape 64x64 pixels, 3-> red, green, blue, activiation is relu
    model.add(Conv2D(32, (3, 3), input_shape = (64, 64, 3), activation = 'relu'))

    # Max pooling with a size of 2x2
    model.add(MaxPooling2D(pool_size = (2, 2)))

    # Add a drop out -> helps prevent of overfitting
    model.add(Dropout(0.2))

    # Repeat of Conv2D and MaxPooling2D
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Dropout(0.2))

    # Flatten -> into 1 dimensional array
    model.add(Flatten())
    # Dense -> hidden layer, fully connected
    model.add(Dense(activation='relu', units=128))

    # We have 5 different units: dancing, running, cycling, yoga or swimming and we are going to use softmax
    model.add(Dense(activation="softmax", units=5))

    # compiling the CNN with the optimizer of adam and the loss with categorical
    model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

    # Print out the summary of our model
    st.write(model.summary())

    # Train your model using the 'epochs' variable
    history = model.fit(training_set,
                        validation_data=validation_set,
                        epochs=epochs)