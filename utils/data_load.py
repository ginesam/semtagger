import re
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import one_hot
from keras.models import Sequential
from keras.layers import Embedding, Flatten, Dense


# very simple classification task! Documents are either good or bad (binary)

def load_glove_embeddings(fp, embedding_dim, include_empty_char=True):
    """
    Loads pre-trained word embeddings (GloVe embeddings)
        Inputs: - fp: filepath of pre-trained glove embeddings
                - embedding_dim: dimension of each vector embedding
                - generate_matrix: whether to generate an embedding matrix
        Outputs:
                - word2coefs: Dictionary. Word to its corresponding coefficients
                - word2index: Dictionary. Word to word-index
                - embedding_matrix: Embedding matrix for Keras Embedding layer
    """
    # First, build the "word2coefs" and "word2index"
    word2coefs = {} # word to its corresponding coefficients
    word2index = {} # word to word-index
    with open(fp) as f:
        for idx, line in enumerate(f):
            try:
                data = [x.strip().lower() for x in line.split()]
                word = data[0]
                coefs = np.asarray(data[1:embedding_dim+1], dtype='float32')
                word2coefs[word] = coefs
                if word not in word2index:
                    word2index[word] = len(word2index)
            except Exception as e:
                print('Exception occurred in `load_glove_embeddings`:', e)
                continue
        # End of for loop.
    # End of with open
    if include_empty_char:
        word2index[''] = len(word2index)
    # Second, build the "embedding_matrix"
    # Words not found in embedding index will be all-zeros. Hence, the "+1".
    vocab_size = len(word2coefs)+1 if include_empty_char else len(word2coefs)
    embedding_matrix = np.zeros((vocab_size, embedding_dim))
    for word, idx in word2index.items():
        embedding_vec = word2coefs.get(word)
        if embedding_vec is not None and embedding_vec.shape[0]==embedding_dim:
            embedding_matrix[idx] = np.asarray(embedding_vec)
    # return word2coefs, word2index, embedding_matrix
    return word2index, np.asarray(embedding_matrix)


# Define documents
docs = ['Well done!', 'Good work', 'Great effort', 'nice work', 'Excellent!',
        'Weak', 'Poor effort!', 'not good', 'poor work', 'Could have done better.']

# Define class labels
labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]

word2index, embedding_matrix = load_glove_embeddings('/home/joan/rug/q2/tfm/src/semtagger/data/embeddings/glove.6B/glove.6B.50d.txt', embedding_dim=50)

# one hot encode documents
def custom_tokenize(docs):
    output_matrix = []
    for d in docs:
        indices = []
        for w in d.split():
            indices.append(word2index[re.sub(r'[^\w\s]','',w).lower()])
        output_matrix.append(indices)
    return output_matrix

# Encode docs with our special "custom_tokenize" function
encoded_docs_ge = custom_tokenize(docs)
print(encoded_docs_ge)

# Pad documents to a max length of 5 words
maxlen = 5
padded_docs_ge = pad_sequences(encoded_docs_ge, maxlen=maxlen, padding='post')
print(padded_docs_ge)


# Define the model
from keras.models import Model
from keras.layers import Input

embedding_layer = Embedding(input_dim=embedding_matrix.shape[0],
                            output_dim=embedding_matrix.shape[1], 
                            input_length=maxlen,
                            weights=[embedding_matrix], 
                            trainable=False, 
                            name='embedding_layer')

i = Input(shape=(maxlen,), dtype='int32', name='main_input')
x = embedding_layer(i)
x = Flatten()(x)
o = Dense(1, activation='sigmoid')(x)

model = Model(inputs=i, outputs=o)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])  # Compile the model
print(model.summary())  # Summarize the model
model.fit(padded_docs_ge, labels, epochs=50, verbose=0)  # Fit the model
loss, accuracy = model.evaluate(padded_docs_ge, labels, verbose=0)  # Evaluate the model
print('Accuracy: %0.3f' % accuracy)





# from Plank
def load_embeddings_file(file_name, sep=" ",lower=False):
    """
    load embeddings file
    """
    emb={}
    for line in open(file_name, errors='ignore', encoding='utf-8'):
        try:
            fields = line.strip().split(sep)
            vec = [float(x) for x in fields[1:]]
            word = fields[0]
            if lower:
                word = word.lower()
            emb[word] = vec
        except ValueError:
            print("Error converting: {}".format(line))

    print("loaded pre-trained embeddings (word->emb_vec) size: {} (lower: {})".format(len(emb.keys()), lower))
    return emb, len(emb[word])

