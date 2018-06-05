Norm's documentation
''''''''''''''''''''''''
.. image:: _static/norm.png
    :scale: 20%

Neural Object Relational Models (NORM) is a probabilistic logical programming language based on neural networks.

Overview
=======================================

When human defines a concept, we mostly compose it with other concepts. For example,

.. image:: _static/jaywalk.jpg
    :scale: 10%
    :align: center

.. code-block:: prolog

    JayWalk{p: Person, r: Road} :-
        WalkCross(p, r) & !On(p, ?z) & ZebraCross(z)


Norm is such a *Probabilistic Logical Programming* language that compiles to neural network
frameworks like Keras and PyTorch and enables high level human-like reasoning.

*Deep Neural Networks* allows accurate and fast optimization with implicit contexts, while *Logical Programming*
allows abstract modeling by human understandable language. Norm marries them together to provide a powerful neural
logical programming experience.

Compositional
------------------
 Norms compose probabilistic models through a logical program where each logical function is a neural network module.

Conversational
------------------
 Norms reason with data scientists interactively to execute query, perform case study, discover new knowledge,
 and improve the intelligence ultimately.


Contents
=======================================

.. toctree::
    :maxdepth: 2

    basic
    interaction
    neuralnet
    indexing
    training
    grammar


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

