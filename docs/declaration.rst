Logic Programming
====================================

Logic programming languages have been out there since very early years. For example,
Prolog is popular in AI field since the 70s. The latest application is in IBM Watson where Prolog
is used to match expert-curated patterns from natural language. Many other languages, like Lisp, Datalog, Erlang,
Curry, and Mercury have been deeply influenced by Prolog.

As a formal language, LP is the closest one to human language. In fact, it has been widely used to construct
semantic theory. For example, Categorial Grammar (CG) considers a linguistic constituent as a
logical function and the semantic meaning of the entire sentence is composed of those functions through combination
rules. Moreover, the declarative paradigm of LP emphasizes the conciseness and preciseness of the communication
instead of the optimality of controlling the execution flow on computers.

Norm borrows the same design principles and focuses on bridging human intelligence and machine intelligence.
This chapter introduces the basic syntax and usage.

Object
------------

Norm objects are essentially a data frame with a relation type. Properties of the type are arguments of the relation plus
several built-in properties.

+------------+----------------------------+------------------+
| Built-in   |Description                 | Value            |
+============+============================+==================+
| prob       |probability                 | [0.0, 1.0]       |
+------------+----------------------------+------------------+
| label      |verified label              | {-1, 0, 1}       |
+------------+----------------------------+------------------+
| tag        |tag                         | 'dead' or etc.   |
+------------+----------------------------+------------------+
| tensor     |tensor representation       |  [0.01,...]      |
+------------+----------------------------+------------------+
| repr       |natural representation      | '<p>example</p>' |
+------------+----------------------------+------------------+

Probability predicts the likelihood of the existence of the relationship. Label is reserved for training purposes.
Any object in Norm has a tensor representation so that logic computation is compiled to neural networks.
Repr provides a human understandable representation in html format to render in frontend, e.g., a web page.
Tag can be used for marking the data, e.g., 'dead' for deleting. These built-in property names are reserved keywords.


Relation
-----------------------------
In Norm, **Type** is equivalent to a **Relation** that declares a relationship among the objects as the arguments. It
evaluates to 1.0 if the relationship exists and is recorded in the world. 0.0 if the relationship does not exists and
is recorded. Otherwise, it evaluates to a probability between $(0.0, 1.0)$ to indicate how likely the relationship
exists in the world.

Any **Relation** can be declared and implemented by composing from other **Relations**. For example, `StockPriceUp` is
a single arity relation of the object referred by the variable `company`. We have a theory that the `company`'s stock
price will go up if it acquired any company which is developing AI technology.

.. code-block:: prolog

    Acquire(company: Company, company_acquired: Company);
    Develop(company: Company, technology: Technology);
    StockPriceUp(company: Company) = Acquire(company, ?comp2) & Develop(comp2, Technology('AI'));

Of course, the accuracy of the theory will be tested against the **World** database. It depends on how accurate
``Acquire`` and ``Develop`` are and how many cases the above theory matches the collected data. Assuming the
**single open world**, the test will sample a certain amount of example companies and exam the fitness. If the test
comes with low accuracy, we can either adapt the parameters or append new theories.


Appending Logic
^^^^^^^^^^^^^^^^^^
Allowing one to append a new theory to the old theory speeds up model development process. For example, if
``Acquire`` means differently for ``microsoft``, we can add the logic to the original **Relation**. If the condition
of ``company == microsoft & Blah`` has little conflict with existing logic, this helps improve the accuracy of the theory.
If conflicts grow, retraining the model parameters mostly help resolve them. Norm supports an **automatic versioning**
feature that any appending logic is considered a new version. In case the modification does not work well, e.g., accuracy
decreases, the **latest** can always rollback to an old one.

.. code-block:: prolog

    Acquire |= company == microsoft & Blah;



Overridden Relation
^^^^^^^^^^^^^^^^^^^^^
The above logic can be considered as an **Overridden Relation** for the `microsoft` object. Another convenient declaration
can be done as the following,

.. code-block:: prolog

    microsoft.Acquire(company_acquired: Company) = Blah;


Function
^^^^^^^^^^
In Norm, **Function** is considered as a special case of a **Relation** where the output is an argument.
Consider the following example where the first statement declares a function that tells which technologies a company
develops. The second statement declares a relation whether a company develops a technology.

.. code-block:: prolog

    Develop1(company: Company): Technology;
    Develop2(company: Company, tech: Technology);


They are equivalent to each other in terms of query (inference) except of the syntax difference.

.. code-block:: prolog

    Develop1(microsoft)?tech == Develop2(microsoft, ?tech);

Function is very convenient for chaining, e.g., extracting features or applying neural network layers.

.. code-block:: prolog

    // Product(name: String, description: String, manufacturer: Company, release_date: DateTime)

    ProductEncoder(product: Product): Dense[float32](100, 300) =
        SentenceEncoder300(sentence=product.description, cutoff=100);
    Develop2(company: Company, tech: Technology) =
        Product(description?desc, manufacturer=company) &
        MLP(Attention(ProductEncoder(desc, tech.tensor))?prob;


Inheritance
^^^^^^^^^^^^

Type inheritance in Norm is considered as a Relation ``IsA(obj: Any, t: Type)`` where ``Any`` means the `obj` can be
of any Type and ``Type`` means that `t` is a Relation variable. If ``IsA`` is satisfied, a ``AsType`` function can
apply on the obj to convert it to a different type. After that, any relation applies to the converted type will be
inherited automatically.

.. code-block:: prolog

    excel = Software('Excel', '', Company('Microsoft'), t'2013-01-01', Platform('Windows'));
    IsA(excel, Product) == 1.0;
    excel.AsType(Product);


Built-in Types
^^^^^^^^^^^^^^^^^^^^

Norm supports some basic types: String, Unicode, Pattern, Integer, Float, DateTime, UUID, URL, and Tensor.

+------------+-------------------------------------------+
| Type       | Constant examples                         |
+============+===========================================+
| String     | 'Amazon Web Service'                      |
+------------+-------------------------------------------+
| Unicode    | u'你好'                                   |
+------------+-------------------------------------------+
| Pattern    | r'\W+'                                    |
+------------+-------------------------------------------+
| Integer    | 23                                        |
+------------+-------------------------------------------+
| Float      | 2.4, 1e-6, -34.55                         |
+------------+-------------------------------------------+
| DateTime   | t'2006-05-16', t'2006'                    |
+------------+-------------------------------------------+
| UUID       | h'1231231441414'                          |
+------------+-------------------------------------------+
| URL        | l'http://www.sphinx-doc.org/en/'          |
+------------+-------------------------------------------+
| Tensor     | [[0,1,2],[2,3,4]]                         |
+------------+-------------------------------------------+


Container Types
^^^^^^^^^^^^^^^^^^

Norm currently only supports a container type: List. Any Relation applies to a List of arguments automatically by
**Vectorization**.


Higher Order Relations
^^^^^^^^^^^^^^^^^^^^^^^

Higher order relations allow Norm to go beyond *propositional logic* and *first order logic*, and fully support
:math:`\lambda`-calculus.

.. code-block:: prolog

    // Perform(person: Person, action: Type)

    actions = [PlayBasketball, WritePaper];
    p = Person('Michael Jordan');
    Perform(p, (action in actions)?f) & f(p, 'NIPS');
    > 1.0, "Michael Jordan writes paper at NIPS"
      0.1, "Michael Jordan plays basketball at NIPS"


Several common higher order functions like Map, Filter and Reduce are handled by **Vectorization**:

.. code-block:: prolog

    // Map(feedbacks, Positive)
    Positive(feedbacks);

    // Filter(feedbacks, Positive)
    Positive(feedbacks) > 0.0;

    // PositiveCount(feedback: Feedback, count: Integer): Integer
    // Reduce(feedbacks, PositiveCount, {0})
    Count(Positive(feedbacks));


Logical Coordinators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Logical coordinators are used for the composition of logical functions. The following table defines all built-in
coordinators for Norm.

+------------+------------+-----------------------+
| Symbol     | Keyword    | Description           |
+============+============+=======================+
| &          | And        | Conjunction           |
+------------+------------+-----------------------+
| \|         | Or         | Disjunction           |
+------------+------------+-----------------------+
| !          | Not        | Negation              |
+------------+------------+-----------------------+
| ^          | Xor        | Exclusive disjunction |
+------------+------------+-----------------------+
| =>         | Imp        | Implication           |
+------------+------------+-----------------------+
| <=>        | Eqv        | Bi-Implication        |
+------------+------------+-----------------------+


Anonymous Relations
^^^^^^^^^^^^^^^^^^^^

Anonymous relations are declared without the type definitions. The properties and their types are inferred according to
unbound variables in the expression. The anonymous relations are not recorded or versioned. It is only effective in the
local scope.

.. code-block:: prolog

    // Inferred as a Relation of (y: Company, x: Company)
    { Develop(y, ?tech) & Develop(x, tech) }

    // Inferred as a constant Relation of value 1.0
    { 1.0 }

Implementation Block
^^^^^^^^^^^^^^^^^^^^^

``{}`` declares an implementation block, the returning objects are composed by picking out the input-output variables.

The one-liners can omit ``{}`` for the simplicity.

Norm allows generic Python implementation by a style comment, ``%python``.

.. code-block:: prolog

    Competing(x: Company, y: Company) = {%python
        techs = norm.demo.Develop(y)
        for tech in techs if norm.demo.Develop(x, tech):
            return (1.0, x, y)
        return (0.0, x, y)
    }

It also allows neural network frameworks like **Keras** and **PyTorch** by ``%keras`` and ``%pytorch``

.. code-block:: prolog

    LSTM(x: Tensor): Tensor = {%keras
        from keras.layers import LSTM
        return LSTM(x)
    }

