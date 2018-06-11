Human Interactions
====================================
How human experts interact with the system is very crucial. Norm aims to deliver an easy and conversational experience
that is able to handle complex modeling tasks. Mutual initiative is the key to streamline the complicated tasks like
model debugging and knowledge discovering.


Data Munging
------------------

Load
^^^^^

It loads data from different sources.

+------------+--------------------------------------------------------------+
| Source     | Example                                                      |
+============+==============================================================+
| mysql      | ``data = load("select * from table", source="mysql")``       |
+------------+--------------------------------------------------------------+
| spark      | ``data = load("select * from table", source="spark")``       |
+------------+--------------------------------------------------------------+
| file       | ``data = load("/tmp/table.csv", source="file", mode="csv")`` |
+------------+--------------------------------------------------------------+
| s3         | ``data = load("bucket/path", source="s3", mode="csv")``      |
+------------+--------------------------------------------------------------+

Insert
^^^^^^^^^^^

It inserts loaded data to a function, e.g., ``Insert(Acquire, data)``. By default, all records from the data become
positive records of ``Acquire``. However, we can set negative records as well by providing annotations, e.g.,
``Insert(Acquire, data, annotations)``, where annotations are a list of floats between [0,1].
It raises conflicts if the data already exists and differs if the policy is **strict**.
The policy could be **overwrite**, **ignore**, **average**, **duplicate** and etc.

Update
^^^^^^^^^^

It updates the function with the data.

Delete
^^^^^^^^

It delete the records from the data, e.g., ``Delete(Acquire(google, microsoft))``


Annotate
^^^^^^^^^^^

It updates the value to a query result, e.g., ``Annotate(Acquire(google, microsoft), False)``, where ``False``
evaluates to 0. Or one can use ``Acquire(google, microsoft) = False`` to annotate a record.


Visualize
^^^^^^^^^^^
It draws graphs for a function, e.g.,

.. code-block:: prolog

    Visualize(Acquire(microsoft, ?comp2, created_on=?time>t'2009') & Develop(comp2, *tech),
              type='trending', y=tech, x=time)


Machine Learning
-----------------

Train
^^^^^^^^

It trains a function using loaded data, e.g., ``Train(Acquire, data, annotations, <other parameters>)``.

Test
^^^^^^

It tests a function using loaded data, e.g., ``Test(Acquire, data, annotations, <other parameters>)``.

Explain
^^^^^^^^

It explains why a function generates such query results

Version Control
----------------

Commit
^^^^^^^

It commits the existing changes to the current session, e.g., ``Commit()`` or ``Commit(Acquire)``.

Rollback
^^^^^^^^^^

It reverts the existing changes to the last commit, e.g., ``Rollback()``.

Merge
^^^^^^

It merges the changes in current session to master, e.g., ``Merge(Acquire)``. If the user is the owner of the function,
it merges automatically. Otherwise, a request is issued to the owner. After the owner review the changes, merge will
proceed



