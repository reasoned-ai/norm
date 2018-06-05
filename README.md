# Norm = "*N*eural *O*bject *R*elational *M*odels"


![alt text](docs/_static/norm-logo.png "Norm Logo")



When human defines a concept, we mostly compose it with other concepts. For example, 

``` norm
JayWalk{p: Person, r: Road} :-
    WalkCross(p, r) & !On(p, ?z) & ZebraCross(z)
``` 

Norm is such a *Probabilistic Logical Programming* language that compiles to neural network
frameworks like Keras and PyTorch and enables high level human-like reasoning.

*Deep Neural Networks* allows accurate and fast optimization, while *Logical Programming* 
allows natural and abstract modeling. Norm marries them together to provide a powerful neural 
logical programming experience.

It delivers the following features:
- **Compositional**: that compose probabilistic models through a logical program 
    where each logical function is a neural network module.
- **Conversational**: that reason with Norms interactively to execute query, perform case study, 
    discover knowledge, and improve models ultimately.

