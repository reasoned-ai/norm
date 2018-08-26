Neural Networks
====================================

In deterministic logic programming, inference is a hard decision. When the logic gets more and more complicated, it
becomes extremely sensitive and brittle. In addition, the conventional logic programming paid more attention to
the context-independent logic in hope that the theorem can be generalized in any situation. This is a rather strong
claim and usually does not hold for real applications. Context-dependent has been proven to be an important complimentary
to symbolic representations. For example, word2vec encodes the context information into a vector for each symbol and has
improved many NLP and text related tasks.

Norm is designed to combine the advantages of both symbolic and numerical representations together,
i.e., **compositional** and **contextual**.

Relation expression
----------------------------

Any relation can be grounded as one neural network like the following example.

.. image:: _static/NN-Norm.png
    :scale: 80%
    :align: center

In this example, light circle represents a free or unobserved variable and dark circle represents a constant or observed
variable. We simply consider ``AND`` as a Multi-Layer Perceptron (MLP) that projects a concatenated vector into a
lower dimensional vector space that is mapped to a probability with a binary entropy loss. The tensor output of the MLP
is taken from a hidden layer.


Sampling
----------------

Assuming an open but single world, all observations are considered as positives. To be able to build a model, one has to
sample the negatives. The entire Norm space is essentially considered as one generative model to sample negative data.


Random Sampling
^^^^^^^^^^^^^^^^

.. code-block:: prolog

    StockPriceUp(company: Company) = Acquire(company, ?comp2) & Develop(comp2, Technology('AI'));


Max-margin Sampling
^^^^^^^^^^^^^^^^^^^^


GAN
^^^^



Training
----------



Weak/distant supervision
--------------------------


Active learning
-------------------


Debugging
-------------------

Indexing
----------

