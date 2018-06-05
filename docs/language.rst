Language
====================================

Prolog is well-known Logical Programming Language from 80s.


Function
-----------------------------
A simple example to show the definition of a norm function composed of other functions


.. code-block:: prolog

   from norm import Acquire, Develop
   StockPriceUp{company: Company} :- Acquire(company, ?(comp2)) & Develop(comp2, 'AI')


`StockPriceUp` is the function name, and `company` is a variable of type `Company`. A function represents a relation
of the objects referred by the variables.


Function has several common attributes:

+--------------+-------------------------------------------------+
| Attributes   | Description                                     |
+==============+=================================================+
| accuracy     | Accuracy metrics, e.g., precision-recall        |
+--------------+-------------------------------------------------+
| performance  | Performance metrics, e.g., latency, throughput  |
+--------------+-------------------------------------------------+
| owner        | Owners of the functions                         |
+--------------+-------------------------------------------------+
| created_on   | Datetime of the creation time                   |
+--------------+-------------------------------------------------+
| version      | Semantic version, <major>.<minor>.<patch>       |
+--------------+-------------------------------------------------+



Logical Operators
^^^^^^^^^^^^^^^^^^
+------------+------------+-----------------------+
| Operator   | Keywords   | Description           |
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


Type
^^^^^^
Type is essentially function too.

.. code-block:: prolog

    Product{name: String, manufacturer: Company, release_date: DateTime}

**Inheritance** can be carried out in the argument declaration. The first example declares that `Software` is a type of
`Product` which needs a platform, e.g., 'Unix'. The second example demonstrates how to curry a function
by providing a value to a parameter.


.. code-block:: prolog

    Software{Product, platform: Platform}
        <=> Software{name: String, manufacturer: Company, release_date: DateTime,
                     platform: Platform}

    MicrosoftSoftware{Product(manufacturer=Company('microsoft')), platform: Platform}
        <=> MicrosoftSoftware{name: String, release_date: DateTime, platform: Platform}


Inheritance indicates an implicit type conversion. The following example shows that `office2003` can be converted to
a product without certainty. However, the other way around produces a low probability.

.. code-block:: prolog

    Sell{vendor: Vendor, product: Product}  # define the relationship that vendor sells a product
    office2003 = MicrosoftSoftware('office2003', DateTime(year=2003), Platform('windows'))
    Sell(dell, office2003)
    > 1.0, Dell Sells Office2003

    OnCloud{cloud: Cloud, software: Software}
    xboxone = Product('xbox one', Company(name='microsoft'), DateTime(year=2012))
    OnCloud(Cloud(name='AWS'), xboxone)
    > 0.0, AWS Sells xbox one

Explicit type conversion can be done by function `AsType`. The default implementation of `AsType` is a projection by
the field name like in the first example. It can be overloaded as in the second example.

.. code-block:: prolog

    xboxone.AsType(Software)
        <=> Software(xboxone.name, xboxone.manufacturer, xboxone.release_date, xboxone.platform)

    xboxone.AsType{type: Type}
    xboxone.AsType |:- (type == Software) & return Software(xboxone.name, Company('fake'),
        xboxone.release_date, None)


Built-in Types
^^^^^^^^^^^^^^^^^^^^
Norm supports some basic types: String, Unicode, Integer, Float, DateTime, UUID, Image, Video, and Tensor.
Norm also supports two containers: Dict and List


Higher order Functions
^^^^^^^^^^^^^^^^^^^^^^^
Norm supports higher order functions like Map, Reduce, Zip and Cross


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
    Join Develop On Develop.company == comp2
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
Norm supports some basic query syntax

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
-----------------------------
Logical function(Type) evaluates to objects.

Object contains several common attributes:

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
