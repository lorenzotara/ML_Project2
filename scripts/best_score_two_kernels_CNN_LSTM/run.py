"""
run.py: This script trains our two kernel-sized CNN_LSTM architecture and then produces the same
csv file used on Kaggle. In our best score we let that the embedding layer
could train the parameters of our word vectors. This process lasted 20 hours
on a windows machine using only CPU (with tensorFlow non optimized for new
generation of CPU's because is not available for windows machines). If you
want to spent less time, CHANGE the value of the variable "trainable" (line 41) to
False and you will obtained our second highest score with this architecture
(85.48) within 3 hours.
"""

__author__    = "Christian Sciuto, Eigil Lippert and Lorenzo Tarantino"
__copyright__ = "Copyright 2017, Second Machine Learning Project, EPFL Machine Learning Course CS-433, Fall 2017"
__credits__   = ["Christian Sciuto", "Eigil Lippert", "Lorenzo Tarantino"]
__license__   = "MIT"
__version_    = "1.0.1"
__status__    = "Project"


from keras import Sequential
from keras.layers import Embedding, Dropout, LSTM, Dense
from helpers import *


# loading our wordVectors
wordVectors = np.load('../../data/our_trained_wordvectors/wordvecs_sg_6.npy')
print('Loaded the word vectors!')

# loading our ids matrix
ids = np.load('../../data/our_trained_wordvectors/ids_sg_6.npy')

# splitting our data in train and test sets
x_train, x_test, y_train, y_test = split_data(ids, 0.9)

print('Build model...')

# Here we define embedding parameters useful for the Embedding Layer
max_features = wordVectors.shape[0]
max_seq_length = ids.shape[1]
embedding_size = wordVectors.shape[1]
trainable = True

# here we define the parameters for the convolutional Layer
# kernel sizes contains the size of the two windows used for grouping words to compute a new feature
filters_shapes = [2, 4]

# the input shape of the input for the convolutional layer
# that is a matrix with rows = number of words in the tweet
# and columns = number of the dimensions of the word vector
input_shape = (max_seq_length, embedding_size)

# filters used in convolutional layer
number_of_filters = 128

# here we define the parameters for the LSTM layer
lstm_output_size = 256

# defining dropout value
if trainable:
    dropout = 0.2
else:
    dropout = 0.1

# here we define parameters for the training
batch_size = 100
epochs = 5

# creating the model structure
model = Sequential()

# First layer, embedding with the pre-trained word vectors, we train on these parameters
model.add(Embedding(max_features, embedding_size, input_length=max_seq_length, weights=[wordVectors],
                    trainable=trainable))

# Prevent overfitting
model.add(Dropout(dropout))

# creating the convolutional layer with different kernel sizes
conv_model = conv_different_kernels(number_of_filters, filters_shapes, max_sentence_length=max_seq_length,
                                    input_dim=input_shape)

model.add(conv_model)

# preventing overfitting
model.add(Dropout(dropout))

# Adding LSTM layer
model.add(LSTM(lstm_output_size))

# adding the final dense layer to reshape and evaluate the y-value
model.add(Dense(1, activation='sigmoid'))

# defining the optimizers. We used the default values
# as suggested on the Keras documentation, we explicitly reported
# them for clarity.
adam_optimizer = keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)

# compiling our model
model.compile(loss='binary_crossentropy',
              optimizer=adam_optimizer,
              metrics=['accuracy'])

# printing the structure of our model
model.summary()

print('Train...')
print(y_train.shape)
print(x_train.shape)

# defining our callback to save metrics in order to create the plots (loss, accuracy)
history = History()

# fitting the model with our train sets

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_data=(x_test, y_test),
          callbacks=[history])

# evaluating our model on the test sets
score, acc = model.evaluate(x_test, y_test, batch_size=batch_size)
print('Test score:', score)
print('Test accuracy:', acc)

# serialize model to JSON
model_json = model.to_json()
with open("run_model.json", "w") as json_file:
    json_file.write(model_json)

# serialize weights to HDF5
model.save_weights("run_weights.h5")
print("Saved model to disk")

# creating the prediction on test set csv file
keras_prediction(model_path="run_model.json",
                 weights_path="run_weights.h5",
                 ids_test_path="../../data/our_trained_wordvectors/ids_test_sg_6.npy",
                 csv_file_name="run_prediction.csv")

# saving the validation accuracy for each epoch
val_acc_epochs = history.epocs_val_acc
np.save("val_acc_two_kernels_CNN_LSTM.npy", val_acc_epochs)

# saving the loss accuracy for each epoch
val_loss_epochs = history.epocs_val_loss
np.save("val_loss_two_kernels_CNN_LSTM.npy", val_loss_epochs)

# here we use our utility function "smooth_graph"
# in order to have smoothed metrics for the plot
smoothed_accuracy = smooth_graph(history.accuracy, 100)

# saving the smoothed metrics
np.save("smoothed_acc_two_kernels_CNN_LSTM.npy", smoothed_accuracy)

# same for the train loss metrics
smoothed_losses = smooth_graph(history.losses, 100)
np.save("smoothed_loss_two_kernels_CNN_LSTM.npy", smoothed_losses)
