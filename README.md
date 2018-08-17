# Norm = {Neural Object Relational Models}


![alt text](docs/_static/norm-logo.png "Norm Logo")


When human defines a concept, we compose it with other concepts. When the concept is not accurate, human critic and
modify the logic of the composition. However, that is not what the state of the arts AI technology, deep learning
practices. Deep neural networks considers the concept as a set of numerical
parameters to be optimized with respect to a set of data and an objective function. This black-box approach is
difficult for regular human experts to interpret and modify. It requires an experienced neural network architect to
fine-tune the parameters constantly.


For example, **JayWalk** is a new concept that we need to detect for *Autonomous Driving Vehicles*. The standard procedure
is to collect a set of positive and negative images, then train a model to classify this concept. The challenge is that
it is difficult to collect positive examples for a complicated concept due to the long tail distribution and the
trained model will be less accurate if the data is not enough. However, if we compose the concept based on other
well-trained concepts, the chance to obtain a high quality model will be increased significantly.

![alt text](docs/_static/jaywalk.png "Jay Walk Example")

``` prolog
    JayWalk(p: Person, r: Road) =
        WalkAcross(p, r) & On(p, z) & Part(r, ?z) & !ZebraCross(z)
```

If some concepts contain errors that accumulate due to the complex compositions, Norm can alleviate this
*brittleness* effectively by adapting the parameters over a small set of examples. The entire logic program is compiled
to a neural network and the power of transfer learning is leveraged.


Representing the AI model in terms of logic forms facilitates the white-box machine learning approach. Domain experts
can understand the logical explanation of the model and can argue with the model by looking into the counter-examples.
Particularly, domain experts can append the **differential logic** to the program and test them out. These explanatory
and explorative debugging capabilities turn the AI model development into an interactive and collaborative process
that fits into most of research agenda in many fields.


In the end, logic program is the closest formal language to human language. Having a natural language parser will enable
many more people to benefit the AI development who do not know how to write in a formal language. It will open a door to
the Artificial General Intelligence that is capable of human-like reasoning.
