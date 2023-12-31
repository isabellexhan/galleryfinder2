#-----------------------------------------------------------------------------
# cnn.py
# Adapted from Yale Digital Humanities Lab's Pixplot project using InceptionV3
#-----------------------------------------------------------------------------
from keras.preprocessing.image import save_img, img_to_array, array_to_img, load_img
from keras.applications.inception_v3 import preprocess_input
from keras.applications import InceptionV3
import os
import glob
import numpy as np
import json
from scipy.spatial.distance import cdist

model = InceptionV3(include_top=False, pooling='avg', weights='imagenet')

# to create static dataset
folder_vectors = []
image_paths = []
base_path = os.path.dirname(os.path.abspath(__file__))

class Image:
    def __init__(self, path):
        self.path = path
        self.original = load_img(self.path) # minimum input size is 75x75

    def get_inception_vector(self, model):
        img = preprocess_input(img_to_array(self.original.resize((299, 299))))
        vec = model.predict(np.expand_dims(img, 0)).squeeze()
        return vec    

# for initializing static dataset
def save_image_paths(image_paths, filename):
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'w') as file:
        json.dump(image_paths, file)

def save_folder_vectors(folder_vectors, filename):
    filepath = os.path.join(base_path, filename)
    np.save(filepath, folder_vectors)

# for using static dataset
def load_image_paths(filename):
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r') as file:
        return json.load(file)

def load_folder_vectors(filename):
    filepath = os.path.join(base_path, filename)
    return np.load(filepath, allow_pickle=True)

# for creating static feature vectors
def store_feature_vectors(folder_path):
    global folder_vectors
    global image_paths
    
    # extract all images from folders within folders
    # jpg specific
    image_paths = glob.glob(os.path.join(folder_path, '**/*.jpg'), recursive=True) 
    folder_images = []
    for path in image_paths:
        image = Image(path)
        folder_images.append(image)
    
    # get feature vectors for images
    for image in folder_images:
        vector = image.get_inception_vector(model)
        folder_vectors.append(vector)
    folder_vectors = np.array(folder_vectors)

    save_image_paths(image_paths, 'medi_image_paths.json')
    save_folder_vectors(folder_vectors, 'medi_folder_vectors.npy')

# add second dataset_path parameter when dynamic
def find_closest_images(input_image_path):
    # Vectorize input image
    input_image = Image(input_image_path)
    input_vector = input_image.get_inception_vector(model)

    # For dynamic dataset: Vectorize dataset images
    # image_paths = glob.glob(os.path.join(folder_path, '*.jpg')) 
    # image_paths = glob.glob(os.path.join(folder_path, '**/*.jpg'), recursive=True) 
    # print("testing: " + str(len(image_paths)))

    # folder_images = []
    # for path in image_paths:
    #     image = Image(path)
    #     folder_images.append(image)
    
    # folder_vectors = []
    # for image in folder_images:
    #     vector = image.get_inception_vector(model)
    #     folder_vectors.append(vector)
    # folder_vectors = np.array(folder_vectors)

    image_paths = load_image_paths('medi_image_paths.json')
    folder_vectors = load_folder_vectors('medi_folder_vectors.npy')
    
    # Calculate cosine similarity
    distances2d = cdist([input_vector], folder_vectors, 'cosine')
    distances = distances2d[0]

    # Return five most similar images
    closest_images_index = np.argsort(distances)
    five_closest = closest_images_index[:5]
    return [image_paths[i] for i in five_closest]

# ran once to create folder vectors and image paths
# path = '../Database/dataset/'
# store_feature_vectors(path)
# print("are we getting here")
# user_image = '../API/temporary.jpg'
# closest_images = find_closest_images(user_image)
# print("Closest images: ", closest_images)