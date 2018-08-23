Inference
===========

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

`?` represents a query of **one** or **some**. `*` represents a query of **any** or **all**.


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

