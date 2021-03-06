# -*- coding: utf-8 -*-
"""Blindness Detector.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ooe4WN6FMWP7ANEgGZOhZQ9XjQecQUcB

# Setting up connection to kaggle
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

# upload the kaggle.json file in order to get data from kaggle API
from google.colab import files
token = files.upload()

import os
os.chdir(r'/content/drive/My Drive/FinalProject')

!mkdir /root/.kaggle/

!cp kaggle.json /root/.kaggle/

!pip install --upgrade pip

!pip uninstall kaggle

!pip install kaggle==1.5.6

!kaggle --version

# upload the dataset to the directory
!kaggle competitions download -c aptos2019-blindness-detection

"""# Mount to Drive"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

import os
os.chdir(r'/content/drive/My Drive/FinalProject')

"""# Preprocessing"""

import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt 
import cv2
from google.colab.patches import cv2_imshow
import numpy as np
import pickle

# !unzip -o 'aptos2019-blindness-detection.zip' -d data/

!pwd

# read the data - first the csv files 
df_train = pd.read_csv('data/train.csv') # dataframe of id_code and diagnosis
df_test = pd.read_csv('data/test.csv')

# let us determine the input (x) and output (y) from training dataset 
# x will be the images
# y will be the diagnosis

X = df_train['id_code']

y = df_train['diagnosis']
y = y.to_numpy()

X_test = df_test['id_code']
X_test = X_test.apply(lambda x: 'data/test_images/' + x + '.png')

!pwd

# add the entire path to the dataframe column id_code
X = X.apply(lambda x: '/content/drive/My Drive/FinalProject/data/train_images/' + x + '.png')

X[0]

y[:5]

# investigate the distribution of the data (diagnosis)
y_train.hist()
y_valid.hist()

# let's have a look at the images now 
def display_img(df, col=4, rows=3):
    fig = plt.figure(figsize=(25,16))
    for i in range(col*rows):
        img_path = df.loc[i, 'id_code']
        img_diag = df.loc[i, 'diagnosis']
        img = cv2.imread(f'data/train_images/{img_path}.png')

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        fig.add_subplot(rows, col, i+1)
        plt.title(img_diag)
        plt.imshow(img)

    plt.tight_layout()

display_img(df_train)

"""We can see that the images are very large. The lighting and the quality differ from each images.

## Convert images to matrix
"""

def to_matrix(series):
  tmp = []
  for img in series:
    # read the image and append it to the training/validation array
    matrix = cv2.imread(img)
    
    # resized = cv2.resize(matrix, (128,128))
    tmp.append(matrix)
  return np.array(tmp)

X_test = to_matrix(X_test)

pickle.dump(X_test, open('./data_test.pkl', 'wb'))

# convert images to matrix
X = to_matrix(X)

# save the matrix inside a pickle file 
pickle.dump(X, open('./vec_train.pkl', 'wb'))

# X.shape

!pwd

# Xx = pickle.load(open('/content/drive/My Drive/FinalProject/vector/data.pkl', 'rb'))
# X_test = pickle.load(open('./data_test.pkl', 'rb'))

def show_single_picture(img):
    """ Plot an image """
    cv2_imshow(img)

# show_single_picture(X[0])

"""## Data Augmentation Steps"""

# tmpX = X_train
tmpX = X
tmpy = y

X_train = tmpX[:2929]
X_valid = tmpX[2929:]

y_train = tmpy[:2929]
y_valid = tmpy[2929:]

from keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(rotation_range=20, zoom_range=0.10,
	horizontal_flip=True,vertical_flip=True)

# Fit data generator on training data for ZCA whitening
datagen.fit(X_train)

# Verify image generated by ImageDataGenerator
for i in  datagen.flow(x=X_train,y=y_train)[0][0]:
  show_single_picture(i)

"""# Model"""

# !tf_upgrade_v2 \
#   --intree my_project/ \
#   --outtree my_project_v2/ \
#   --reportfile report.txt

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pickle 
import datetime
from sklearn.model_selection import train_test_split
import pandas as pd 

# Using pre-trained models
from keras.applications import VGG16, VGG19, InceptionResNetV2, Xception, NASNetLarge
from keras import datasets, optimizers
from keras.layers import Conv2D, Dropout, Dense, Flatten, MaxPooling2D, Input, GlobalAveragePooling2D
from keras.models import Model, Sequential, load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import DenseNet121,DenseNet169,DenseNet201

# Initialize optimizer
learning_rate = 0.01
optimizer = optimizers.SGD(lr=learning_rate, decay=1e-6, momentum=0.9)

# optimizer = optimizers.RMSprop(lr=learning_rate)

# optimizer = optimizers.Adam(lr=learning_rate)

# Initialize number of epochs, batch_size and validation split 
WARMUP = 5
EPOCHS = 30
batch_size = 32

# image_size = 512
# num_channels = 3

image_size = 128
num_channels = 3

# X.shape

# VGG 16 
# Create a model using pretrained VGG16
base_model = VGG16(weights='imagenet', include_top=False, input_tensor=Input(shape=(image_size, image_size, num_channels)), pooling='avg') # assumes data_format = "channels_last"

# base_model = VGG16(weights='imagenet', include_top=False, input_tensor=Input(shape=(image_size, image_size, num_channels)), pooling='avg') # assumes data_format = "channels_last"


# Add a global spatial average pooling layer
top_network = base_model.output
# Add a fully-connected layer    
top_network = Dense(128, activation='relu')(top_network)
# Add a Dropout layer
top_network = Dropout(0.25)(top_network)

# Add a fully-connected layer    
top_network = Dense(64, activation='relu')(top_network)

# Add a logistic layer with 10 classes
top_network = Dense(5, activation='softmax')(top_network)

# Create model
model = Model(inputs=base_model.input, outputs=top_network)

# Compile the model (should be done ***after*** setting layers to non-trainable)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=["accuracy"])

# Print a summary of the model
model.summary()

# Initialize optimizer
learning_rate = 1e-3
optimizer = optimizers.SGD(lr=learning_rate, momentum=0.9)


last_model = load_model('VGG16.h5')

""" Model with datagen """
history2 = model.fit_generator(datagen.flow(x=X_train, y=y_train, batch_size=batch_size), validation_data=(X_valid,y_valid), epochs=10, shuffle=True, steps_per_epoch=len(X_train)//batch_size)

# gpu_options = tf.GPUOptions(allow_growth=True)
# session = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options))

# Assume that you have 12GB of GPU memory and want to allocate ~4GB:
# gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)

# sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
""" model without Datagen """
history = model.fit(x=X, y=y, epochs=10, validation_split=0.2,shuffle=True, use_multiprocessing=True)

# save the trained model 
model.save('VGG16_imagegen.h5')

model.lomodel.save_weights('VGG16_imagegen_weights.h5')

# Plot history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

y_pred = last_model.predict(X_test)

y_pred = last_model.predict(X_test)

y= []
for pred in y_pred:
  
  pred = list(pred)
  pr = pred.index((max(pred)))

  y.append(pr)

import csv
with open('submission.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['ID', 'label'])

    for i in range(len(y)):
      writer.writerow((df_test['id_code'][i], y[i]))