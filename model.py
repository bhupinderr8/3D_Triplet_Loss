import numpy as np
from keras import backend as K
from keras.models import Model
import tensorflow as tf
from keras.layers import (Activation, Conv3D, Dense, Dropout, Flatten, MaxPooling3D, concatenate, Input, BatchNormalization, MaxPool3D)
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from keras.utils.vis_utils import plot_model


nb_classes = 5
edge_size = 32
nb_pairs = 75
X = np.load('X_Data.npy')
print(X.shape)
Y = np.load('Y_Data.npy')


def accuracy(y_true, y_pred):
    embeddings = K.reshape(y_pred, (-1, 3, nb_classes))
    positive_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 1]), axis=-1)
    negative_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 2]), axis=-1)
    return positive_distance

def p_dis(y_true, y_pred):
    embeddings = K.reshape(y_pred, (-1, 3, nb_classes))
    positive_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 1]), axis=-1)
    return positive_distance


def n_dis(y_true, y_pred):
    embeddings = K.reshape(y_pred, (-1, 3, nb_classes))
    negative_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 2]), axis=-1)
    return negative_distance


def triplet_loss(y_true, y_pred, alpha=0.2):
    embeddings = K.reshape(y_pred, (-1, 3, nb_classes))

    positive_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 1]), axis=-1)
    negative_distance = K.mean(K.square(embeddings[:, 0] - embeddings[:, 2]), axis=-1)
    return K.mean(K.maximum(0.0, positive_distance - negative_distance + alpha))


a = Input(shape=(32, 32, 32, 1))
p = Input(shape=(32, 32, 32, 1))
n = Input(shape=(32, 32, 32, 1))

model = Sequential()
model.add(Conv3D(32, kernel_size=(3, 3, 3), input_shape=(32, 32, 32, 1), border_mode='same'))
model.add(Activation('relu'))
model.add(Conv3D(32, kernel_size=(3, 3, 3), border_mode='same'))
model.add(Activation('softmax'))
model.add(MaxPooling3D(pool_size=(3, 3, 3), border_mode='same'))
model.add(Dropout(0.25))
model.add(Conv3D(64, kernel_size=(3, 3, 3), border_mode='same'))
model.add(Activation('relu'))
model.add(Conv3D(64, kernel_size=(3, 3, 3), border_mode='same'))
model.add(Activation('relu'))
model.add(MaxPooling3D(pool_size=(3, 3, 3), border_mode='same'))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(512, activation='sigmoid'))
model.add(Dense(nb_classes, activation='relu'))
model.add(BatchNormalization())


model_2 = Sequential()
model_2.add(Conv3D(32, kernel_size=(3, 3, 3), input_shape=(32, 32, 32, 1), border_mode='same'))
model_2.add(MaxPool3D())
model_2.add(Conv3D(32, kernel_size=(1, 1, 1), border_mode='same'))
model_2.add(Activation('relu'))
model_2.add(Conv3D(32, kernel_size=(3, 3, 3), border_mode='same'))
model_2.add(Conv3D(32, kernel_size=(3, 3, 3), border_mode='same'))
model_2.add(Conv3D(32, kernel_size=(3, 3, 3), border_mode='same'))
model_2.add(MaxPool3D())
model_2.add(Dropout(0.25))
model_2.add(Flatten())
model_2.add(Dense(512, activation='relu'))
model_2.add(Dense(nb_classes, activation='relu'))
model_2.add(BatchNormalization())
model_2.summary()
model_a = model_2(a)
model_p = model_2(p)
model_n = model_2(n)
# model.summary()
loss = concatenate([model_a, model_n, model_p])
model_f = Model(input=[a, p, n], output=loss)
model_f.compile(loss=triplet_loss, optimizer='adam', metrics=[p_dis, n_dis])
# model_f.summary()
callb = ModelCheckpoint(filepath='model.hdf5', monitor='val_loss', verbose=0, save_best_only=False, save_weights_only=False, mode='auto', period=1)
# model_f.load_weights('model.hdf5')
model_f.fit(x=[X[:, 0, :, :, :].reshape(nb_pairs, edge_size, edge_size, edge_size, 1),
               X[:, 1, :, :, :].reshape(nb_pairs, edge_size, edge_size, edge_size, 1),
               X[:, 2, :, :, :].reshape(nb_pairs, edge_size, edge_size, edge_size, 1)],
            y=Y,
            epochs=20,
            batch_size=25,
            callbacks=[callb])

# plot_model(model_f, to_file='model_plot.png', show_shapes=True, show_layer_names=True)