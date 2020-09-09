"""
Created on August 3, 2020

model: Attentional Factorization Machines: Learning the Weight of Feature Interactions via Attention Networks

@author: Ziyao Geng
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Embedding, Dropout, Concatenate, Dense, Input, GlobalMaxPooling1D, GlobalAveragePooling1D


class AFM(keras.Model):
    def __init__(self, feature_columns, mode, attention_hidden_unit=64, embed_reg=1e-4):
        """
        AFM architecture
        :param feature_columns: dense_feature_columns and sparse_feature_columns
        :param mode: 'max'(MAX Pooling) or 'avg'(Average Pooling) or 'att'(Attention)
        :param attention_hidden_unit: hidden unit, if mode == 'att'
        :param embed_reg: the regularizer of embedding
        """
        super(AFM, self).__init__()
        self.dense_feature_columns, self.sparse_feature_columns = feature_columns
        self.mode = mode
        self.embed_layers = {
            'embed_' + str(i): Embedding(input_dim=feat['feat_num'],
                                         input_length=1,
                                         output_dim=feat['embed_dim'],
                                         embeddings_initializer='random_uniform',
                                         embeddings_regularizer=l2(embed_reg))
            for i, feat in enumerate(self.sparse_feature_columns)
        }
        if self.mode == 'max':
            self.max = GlobalMaxPooling1D()
        elif self.mode == 'avg':
            self.avg = GlobalAveragePooling1D()
        else:
            self.attention_dense = Dense(units=attention_hidden_unit, activation='relu')
            self.attention_dense2 = Dense(units=1, activation=None)

        self.dense = Dense(units=1, activation=None)
        self.concat = Concatenate(axis=-1)

    def call(self, inputs):
        # Input Layer
        dense_inputs, sparse_inputs = inputs
        # Embedding Layer
        embed = [self.embed_layers['embed_{}'.format(i)](sparse_inputs[:, i]) for i in range(sparse_inputs.shape[1])]
        embed = tf.transpose(tf.convert_to_tensor(embed), [1, 0, 2])
        # Pair-wise Interaction Layer
        # for loop is badly
        element_wise_product_list = []
        for i in range(embed.shape[1]):
            for j in range(i+1, embed.shape[1]):
                element_wise_product_list.append(tf.multiply(embed[:, i], embed[:, j]))
        element_wise_product = tf.transpose(tf.concat(element_wise_product_list), [1, 0, 2])
        # mode
        if self.mode == 'max':
            # MaxPooling Layer
            x = self.max(element_wise_product)
        elif self.mode == 'avg':
            # AvgPooling Layer
            x = self.avg(element_wise_product)
        else:
            # Attention Layer
            x = self.attention(element_wise_product)
        # Concatenate Layer
        x = self.concat([dense_inputs, x])
        # Output Layer
        outputs = tf.nn.sigmoid(self.dense(x))
        return outputs

    def summary(self):
        dense_inputs = Input(shape=(len(self.dense_feature_columns),), dtype=tf.float32)
        sparse_inputs = Input(shape=(len(self.sparse_feature_columns),), dtype=tf.int32)
        keras.Model(inputs=[dense_inputs, sparse_inputs], outputs=self.call([dense_inputs, sparse_inputs])).summary()

    def attention(self, keys):
        a = self.attention_dense(keys)
        a = self.attention_dense2(a)
        a_score = tf.nn.softmax(a)
        a_score = tf.transpose(a_score, [0, 2, 1])
        outputs = tf.reshape(tf.matmul(a_score, keys), shape=(-1, keys.shape[2]))
        return outputs
