'''Train a recurrent convolutional network on the IMDB sentiment
classification task.
Gets to 0.8498 test accuracy after 2 epochs. 41s/epoch on K520 GPU.
'''
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import LSTM
from keras.layers import Conv1D, MaxPooling1D
from keras.datasets import imdb
import numpy as np
import re
from random import randint

def clean_sentences(string):
    string = string.lower().replace("<br />", " ")
    return re.sub(strip_special_chars, "", string.lower())


# def get_train_batch():
#     labels = []
#     arr = np.zeros([batch_size, max_seq_length])
#     for i in range(batch_size):
#         if (i % 2 == 0):
#             # num = randint(1, len(positive_files))
#             # Leaving 750*2 samples for testing
#             num = randint(1, len(positive_files) - 750)
#             labels.append([1, 0])
#         else:
#             # num = randint(len(positive_files)+1, len(positive_files)+len(negative_files))
#             # Leaving 750*2 samples for testing
#             num = randint(len(positive_files)+750, len(positive_files)+len(negative_files))
#             labels.append([0, 1])
#         arr[i] = ids[num-1:num]
#     return arr, labels
#
#
# def get_test_batch():
#     labels = []
#     arr = np.zeros([batch_size, max_seq_length])
#     for i in range(batch_size):
#         num = randint(len(positive_files) - 750, len(positive_files) + 750)
#         if num <= len(positive_files):
#             labels.append([1, 0])
#         else:
#             labels.append([0, 1])
#         arr[i] = ids[num-1:num]
#     return arr, labels


def split_data(x, ratio, seed=1):
    """split the dataset based on the split ratio."""

    y = np.array([1] * int(x.shape[0]/2))
    y = np.append(y, np.array([0] * int(x.shape[0]/2)))
    # set seed
    np.random.seed(seed)
    # generate random indices
    num_row = x.shape[0]
    indices = np.random.permutation(num_row)
    index_split = int(np.floor(ratio * num_row))
    index_tr = indices[: index_split]
    index_te = indices[index_split:]
    # create split
    x_tr = x[index_tr]
    x_te = x[index_te]
    y_tr = y[index_tr]
    y_te = y[index_te]
    return x_tr, x_te, y_tr, y_te

# Removes punctuation, parentheses, question marks, etc., and leaves only alphanumeric characters
strip_special_chars = re.compile("[^A-Za-z0-9 ]+")



'''
Note:
batch_size is highly sensitive.
Only 2 epochs are needed as the dataset is very small.
'''

# print('Loading data...')
# (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)
# print(len(x_train), 'train sequences')
# print(len(x_test), 'test sequences')
# print(x_train[0])
# print(x_train.shape)
# print('\n\n')
# # print(type(x_train)) = <class 'numpy.ndarray'>
#
# print('Pad sequences (samples x time)')
# x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
# print(x_train[0])
# print(x_train.shape)
# x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
# # print('x_train shape:', x_train.shape)
# print('x_test shape:', x_test.shape)

path_positive = "data/twitter-datasets/train_pos.txt"
path_negative = "data/twitter-datasets/train_neg.txt"

numWords = []
positive_files_total = []
negative_files_total = []
with open(path_positive, "r") as f:
    for line in f:
        positive_files_total.append(line)
        counter = len(line.split())
        numWords.append(counter)


with open(path_negative, "r", encoding='utf-8') as f:
    for line in f:
        negative_files_total.append(line)
        counter = len(line.split())
        numWords.append(counter)


num_files_total = len(numWords)
print('The total number of files is', num_files_total)
print('The total number of words in the files is', sum(numWords))
print('The average number of words in the files is', sum(numWords)/len(numWords))

# plt.hist(numWords, 50)
# plt.xlabel('Sequence Length')
# plt.ylabel('Frequency')
# plt.axis([0, 40, 0, 25000])
# plt.show()



wordsList = np.load('wordsList.npy')
print('Loaded the word list!')
wordsList = wordsList.tolist()  # Originally loaded as numpy array
wordsList = [word.decode('UTF-8') for word in wordsList]  # Encode words as UTF-8
wordVectors = np.load('wordVectors.npy')
print('Loaded the word vectors!')

positive_files = positive_files_total
negative_files = negative_files_total
num_files_mini = len(positive_files) + len(negative_files)

ids = np.load('ids_final.npy')
# ids = np.load('ids_train_not_full.npy')

x_train, x_test, y_train, y_test = split_data(ids, 0.8)

print('Build model...')

# Embedding
# number of words in the word vectors
max_features = 400000
max_seq_length = int(sum(numWords)/len(numWords)) + 5
# embedding_size = 128  # first time
embedding_size = 50

# Convolution
kernel_size = 5
filters = 64
pool_size = 4

# LSTM
lstm_output_size = 64

# Training
batch_size = 50
epochs = 5

model = Sequential()
# First layer, embedding
# model.add(Embedding(max_features, embedding_size, input_length=max_seq_length))  # w\o wordVectors - old one
# model.add(Embedding(max_features, embedding_size, weights=[wordVectors], input_length=max_seq_length))
# TODO: To try
model.add(Embedding(max_features, embedding_size, weights=[wordVectors], input_length=max_seq_length, trainable=False))
# Prevent overfitting
model.add(Dropout(0.25))
# First real layer, convolutional layer
model.add(Conv1D(filters,
                 kernel_size,
                 padding='valid',
                 activation='relu',
                 strides=1,
                 use_bias=False))
# Ask Christian
model.add(MaxPooling1D(pool_size=pool_size))
# Prevent overfitting
model.add(Dropout(0.25))
# Adding LSTM layer
model.add(LSTM(lstm_output_size))
# Dense implements the operation: output = activation(dot(input, kernel) + bias) where activation is the element-wise
# activation function passed as the activation argument, kernel is a weights matrix created by the layer, and bias is a
# bias vector created by the layer (only applicable if use_bias is True).
model.add(Dense(1))
'''
# model.add(Dense(64))
# model.add(Activation('tanh'))
This is equivalent to
# model.add(Dense(64, activation='tanh'))
'''
model.add(Activation('sigmoid'))
'''
metrics: List of metrics to be evaluated by the model during training and testing. Typically you will use 
metrics=['accuracy']. To specify different metrics for different outputs of a multi-output model, you could also pass a 
dictionary, such as metrics={'output_a': 'accuracy'}.
'''
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

print('Train...')
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_data=(x_test, y_test))
score, acc = model.evaluate(x_test, y_test, batch_size=batch_size)
print('Test score:', score)
print('Test accuracy:', acc)

# serialize model to JSON
model_json = model.to_json()
with open("crnn1_model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("crnn1_weights.h5")
print("Saved model to disk")