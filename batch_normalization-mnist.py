import tensorflow as tf
import numpy as np

(X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()
X_train = X_train.astype(np.float32).reshape(-1, 28*28) / 255.0
X_test = X_test.astype(np.float32).reshape(-1, 28*28) / 255.0
y_train = y_train.astype(np.int32)
y_test = y_test.astype(np.int32)
X_valid, X_train = X_train[:5000], X_train[5000:]
y_valid, y_train = y_train[:5000], y_train[5000:]

def reset_graph(seed=42):
    tf.reset_default_graph()
    tf.set_random_seed(seed)
    np.random.seed(seed)
    
def shuffle_batch(X, y, batch_size):
    rnd_idx = np.random.permutation(len(X))
    n_batches = len(X) // batch_size
    for batch_idx in np.array_split(rnd_idx, n_batches):
        X_batch, y_batch = X[batch_idx], y[batch_idx]
        yield X_batch, y_batch

reset_graph()
n_inputs = 28 * 28 # image size
n_hidden1 = 300 
n_hidden2 = 100
n_outputs = 10
learning_rate = 0.01

n_epochs = 25
batch_size = 250

X = tf.placeholder(tf.float32, shape=(None, n_inputs), name="X")
y = tf.placeholder(tf.int32, shape=(None), name="y")
training = tf.placeholder_with_default(False, shape=(), name='training')

with tf.name_scope("dnn"):
    hiddenLayer1 = tf.layers.dense(X, n_hidden1, name="hidden1")
    batchNorm1 = tf.layers.batch_normalization(hiddenLayer1, training=training, momentum=0.9)
    batchNorm1_act = tf.nn.elu(batchNorm1) # ELU Activation

    hiddenLayer2 = tf.layers.dense(batchNorm1_act, n_hidden2, name="hidden2")
    batchNorm2 = tf.layers.batch_normalization(hiddenLayer2, training=training, momentum=0.9)
    batchNorm2_act = tf.nn.elu(batchNorm2)

    logits = tf.layers.dense(batchNorm2_act, n_outputs, name="outputs")
    logits_batchNorm = tf.layers.batch_normalization(logits, training=training, momentum=0.9)

with tf.name_scope("loss"):
    x_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits)
    loss = tf.reduce_mean(x_entropy, name="loss")
    
with tf.name_scope("optimize"):
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    training_ops = optimizer.minimize(loss)
    
with tf.name_scope("eval"):
    correct = tf.nn.in_top_k(logits, y, 1)
    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

init = tf.global_variables_initializer()
saver = tf.train.Saver()

extra_graphkeys_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

with tf.Session() as sess:
    init.run()
    for epoch in range(n_epochs):
        for X_batch, y_batch in shuffle_batch(X_train, y_train, batch_size):
            sess.run([training_ops, extra_graphkeys_update_ops],
                     feed_dict={training: True, X: X_batch, y: y_batch})
        accuracy_val = accuracy.eval(feed_dict={X: X_valid, y: y_valid})
        print(epoch+1, "Validation accuracy:", accuracy_val)

    save_path = saver.save(sess, "./mnist-batch-normalized-model.ckpt")
