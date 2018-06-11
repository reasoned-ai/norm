Logical Programming
====================================

Logical programming language has been out since very early years. For example,
Prolog is very popular in AI field since 70s. The latest large scale application is in IBM Watson where Prolog
is used to match expert curated patterns from natural language. Many other languages, like Lisp, Datalog, Erlang,
Curry, and Mercury have been deeply influenced by Prolog.

As a formal language, LP is the closest one to human language. In fact, it has been widely used to construct
semantic theory. For example, Categorial Grammar (CG) considers a linguistic constituent as a
logical function and the semantic meaning of the entire sentence is composed by those functions through combination
rules. Moreover, the declarative paradigm of LP emphasizes the conciseness and preciseness of the communication
instead of the optimality of controlling the execution flows on computers.

Norm borrows the same design principles and focuses on bridging human intelligence and machine intelligence.
This chapter introduces the basic syntax and usage.


Function & Type
-----------------------------
From the typological point of view, function and type refers the same concept that declares a relation among objects.
It evaluates to *True* if the relation exists, *False* otherwise. The implementation of a relation is defined by
**composition**. The following example shows how to compose a Norm function from other functions.


.. code-block:: prolog

    namespace norm.demo

    Acquire(company: Company, company_acquired: Company)
    Develop(company: Company, technology: Technology)
    StockPriceUp(company: Company) :- { Acquire(company, ?(comp2)) & Develop(comp2, 'AI') }


In this example, `StockPriceUp` is a function name, and `company` is a variable of type `Company`. `?(comp2)` represents
a **existential quantifier** or **skolemization**.

Norm allows two convenient function declarations.


.. code-block:: prolog

    microsoft.Acquire(company_acquired: Company) => Acquire(microsoft, company_acquired: Company)
    Develop(company: Company): Technology => Develop(company: Company, _: Technology)


The first example shows that functions can be attached to a particular object. This allows function **overloading**,
i.e., an implementation for the case of microsoft being the acquirer could be different than other companies.

The second example defines a function outputs a *Technology* object to an implicit variable `_`. This restricts the
function to only produce results for the last parameter, i.e., ``Develop(?company, 'AI')`` raises error. Conventional
functional programming only takes this form of function declarations. It is useful for functions to extract features
like neural network functions or patterns like regex functions.


Inheritance
^^^^^^^^^^^^

Type inheritance in Norm is carried out through declaration like the following examples:

.. code-block:: prolog

    Product(name: String, manufacturer: Company, release_date: DateTime)

    Software(Product, platform: Platform)
        <=> Software(name: String, manufacturer: Company, release_date: DateTime,
                     platform: Platform)

    MicrosoftSoftware(Product{manufacturer=Company('microsoft')}, platform: Platform)
        <=> MicrosoftSoftware(name: String, release_date: DateTime, platform: Platform)

The first example declares that `Software` is a type of `Product` which needs a platform, e.g., 'Unix'.
The second example demonstrates how to curry a function by providing a value to a parameter.

Inheritance indicates an implicit type conversion. The following example shows that `office2003` can be converted to
a product with a high probability. However, the other way around produces a low probability.

.. code-block:: prolog

    Sell(vendor: Vendor, product: Product)  # define the relationship that vendor sells a product
    office2003 = MicrosoftSoftware('office2003', DateTime(year=2003), Platform('windows'))
    Sell(dell, office2003)
    > 1.0, Dell Sells Office2003

    OnCloud(cloud: Cloud, software: Software)
    xboxone = Product('xbox one', Company(name='microsoft'), DateTime(year=2012))
    OnCloud(Cloud(name='AWS'), xboxone)
    > 0.0, AWS Sells xbox one

Explicit type conversion can be done by function `AsType`. The default implementation of `AsType` is a projection by
the field name like in the first example. It can be overloaded as in the second example.

.. code-block:: prolog

    xboxone.AsType(Software)
        <=> Software(xboxone.name, xboxone.manufacturer, xboxone.release_date, xboxone.platform)

    xboxone.AsType(type: Type)
    xboxone.AsType |:- (type == Software) & return Software(xboxone.name, Company('fake'),
        xboxone.release_date, None)


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
| Tensor     | m[[0,1,2],[2,3,4]]                        |
+------------+-------------------------------------------+

Norm also supports a container type: List


Higher Order Functions
^^^^^^^^^^^^^^^^^^^^^^^

Higher order functions allow Norm to go beyond *propositional logic* and *first order logic*, and fully support
$\lambda$ calculus.

.. code-block:: prolog

    actions = [PlayBasketball(person: Person), WritePaper(person: Person)]
    Perform(person: Person, action: Type)

    p = Person('Michael Jordan')
    Perform(p, ?(f in actions)) & f(p)
    > 1.0, WritePaper
      0.1, PlayBasketball


Norm also supports several built-in higher order functions:

+-----------------------------------------------+----------------------------------------------------------------------------+
| Higher order function                         | Description                                                                |
+===============================================+============================================================================+
| Map(list: List, func: Type): List             | Apply func on all elements in the list and return a list of new objects    |
+-----------------------------------------------+----------------------------------------------------------------------------+
| Filter(list: List, func: Type): List          | Apply func on all elements in the list and return a list of old objects    |
+-----------------------------------------------+----------------------------------------------------------------------------+
| Reduce(list: List, func: Type, init: Type)    | Apply func sequentially on all elements and return an object               |
+-----------------------------------------------+----------------------------------------------------------------------------+

.. code-block:: prolog

    Map(feedbacks, Positive) <=> Positive(feedbacks)
    Filter(feedbacks, Positive) <=> Feedback*(feedback) & Positive(feedback)
    PositiveCount(feedback: Feedback, count: Integer): Integer
    Reduce(feedbacks, PositiveCount, {0}) <=> (Feedback*(feedback) & Positive(feedback)).Count()


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

Norm allows incremental implementations, for example, we previously implemented `StockPriceUp`. After inspections on
training and testing errors, we would like to add more logic to test more hypothesis.

.. code-block:: prolog

    StockPriceUp |:- { Acquire(company, ?(comp2)) & Develop(comp2, 'Blockchain') }


Anonymous Functions
^^^^^^^^^^^^^^^^^^^^

`() :- {}` allows an anonymous function to be declared and used in the local scope, i.e., they can not be shared.

.. code-block:: prolog

    (x: Company, y: Company) :- { Develop(y, ?tech) & Develop(x, tech) }
    { 1.0 } # a function returns the constant 1.0

Implementation Block
^^^^^^^^^^^^^^^^^^^^^

`{}` declares an implementation block, the returning object is composed by picking out the input-output variables.
A neural network-based implementation allows the computation to be carried out in parallel. Multiple exits imply
preemptive interruption which might not be necessary. Hence functions implemented in neural network,
i.e., the normal functions don't support multiple exits.

However, it allows generic Python implementation by a style comment, `%python`.

.. code-block:: prolog

    (x: Company, y: Company) :- {%python
        techs = norm.demo.Develop(y)
        for tech in techs:
            if norm.demo.Develop(x, tech):
                return (1.0, x, y)
        return (0.0, x, y)
    }

A neural network function computes tensors from other tensors which can be implemented by Keras or PyTorch, `%keras` or
`%pytorch`.

.. code-block:: prolog

    (x: Tensor, y: Tensor) :- {%keras
        from keras.layers import LSTM
        y = LSTM(x)
    }


Query
-----------------------------
Query is one fundamental capability of Norm functions. ``Acquire(microsoft, ?(comp2))`` represents
a query in SQL. The query result returns the value for the variable and the relevance score.

.. code-block:: sql

    Select company2 as comp2
    From Acquire
    Where company1 = microsoft.id
    Limit 1

    > 1.0, Semantic Machines

If the database returns a record, the logical function resolves to True. The variable ``comp2`` is assigned
the object retrieved.
If the database does not have such a record, the logical function resolves to False, and the evaluation is terminated.

For the query of ``Acquire(microsoft, ?4(comp2)) & Develop(comp2, 'AI')`` represents a query to get up to 4 records

.. code-block:: sql

    Select company2 as comp2
    From Acquire
    Join Develop On Develop.company = comp2
    Where company1 = microsoft.id and Develop.technology = 'AI'
    Limit 4

    > 1.0, Semantic Machines
      1.0, Maluuba
      1.0, LinkedIn
      1.0, Genee

We can also evaluate the function by setting the query at the end. For example, ``Acquire(microsoft, linkedin)?``.

.. code-block:: sql

    Select *
    From Acquire
    Where company1 = microsoft.id and company2 = linkedin.id
    Limit 1

    > 1.0, Microsoft acquired LinkedIn in 2016

The resolution is an object if the record exists. Otherwise, it resolves to None. For query up to 1 record, '?' is
optional.

Query Syntax
^^^^^^^^^^^^^
A query is represented by `?<limit><var><constraints>`. Norm supports some basic constraint syntax

+------------+--------------------+-----------------------------+
| Operator   | Keywords           | Description                 |
+============+====================+=============================+
| >          | gt                 | Greater than                |
+------------+--------------------+-----------------------------+
| >=         | ge                 | Greater than or equal to    |
+------------+--------------------+-----------------------------+
| <          | lt                 | Less than                   |
+------------+--------------------+-----------------------------+
| <=         | le                 | Less than or equal to       |
+------------+--------------------+-----------------------------+
| ==         | eq                 | Equal                       |
+------------+--------------------+-----------------------------+
| !=         | neq                | Not equal                   |
+------------+--------------------+-----------------------------+
| in         | in                 | Check the existence         |
+------------+--------------------+-----------------------------+
| ~          | like               | fuzzy match                 |
+------------+--------------------+-----------------------------+


Probabilistic Query
^^^^^^^^^^^^^^^^^^^^^
As a probabilistic model, Norm supports probabilistic query when no exactly matched records found.

.. code-block:: prolog

    Develop('Revolution Analytics', 'AI')
    > 0.6, Revolution Analytics develops Artificial Intelligence technology

    Develop('Revolution Analytics', ?5)
    > 1.0, Analytics
      1.0, R
      1.0, Statistics
      0.8, Machine Learning
      0.6, Artificial Intelligence


Object
^^^^^^^^
Logical function(Type) evaluates to objects and each contains several common attributes.

+--------------+-------------------------------------------------+
| Attributes   | Description                                     |
+==============+=================================================+
| prob         | Probability of being True                       |
+--------------+-------------------------------------------------+
| repr         | Human understandable utterance representation   |
+--------------+-------------------------------------------------+
| html         | Human understandable visual representation      |
+--------------+-------------------------------------------------+
| tensor       | Machine understandable tensor                   |
+--------------+-------------------------------------------------+

Tensor attribute is used implicitly to build neural networks. Beneath the composition of logical functions, tensors of
the objects are fed to the neural networks, the output tensor is bound to the object's tensor attribute. Domain expert
builds models through logical functions, but compiles to neural networks.


List of objects
^^^^^^^^^^^^^^^^^
List supports a few aggregation function.

+--------------+-------------------------------------------------+
| Function     | Description                                     |
+==============+=================================================+
| Max          | Maximum probable object                         |
+--------------+-------------------------------------------------+
| Min          | Minimum probable object                         |
+--------------+-------------------------------------------------+
| Ave          | Averaged object by the probability              |
+--------------+-------------------------------------------------+
| Count        | Total number of all objects                     |
+--------------+-------------------------------------------------+
| Group        | Group objects by a column or the tensor         |
+--------------+-------------------------------------------------+
| Unique       | Unique objects by columns                       |
+--------------+-------------------------------------------------+

In deterministic sense, these aggregation function map to the SQL equivalent. In probabilistic sense, `Max` usually
is considered as **MAP** inference, while `Ave` is essentially a **marginalization**. The interesting thing is the
repr or html for the marginalized object. **Summarization** for images can be done through technique like *EigenFace*.
For text, a generative model is required to produce a reasonable results which is still an active research topic.

`Group` by the tensor can be simply carried out by **k-means**, but more advanced clustering technology yield better
results.

