Interactions
====================================

Data
------------------

load
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

insert
^^^^^^^^^^^

It inserts loaded data to a function, e.g., ``insert(Acquire, data)``. By default, all records from the data become
positive records of ``Acquire``. However, we can set negative records as well by providing annotations, e.g.,
``insert(Acquire, data, annotations)``, where annotations are a list of floats between [0,1].
It raises conflicts if the data already exists and differs if the policy is **strict**.
The policy could be **overwrite**, **ignore**, **average**, **duplicate** and etc.

annotate
^^^^^^^^^^^

It updates the value to a query result, e.g., ``annotate(Acquire(google, microsoft), False)``, where ``False=>0``.

visualize
^^^^^^^^^^^
It draws graphs for a function


Modeling
---------

train
^^^^^^^^

It trains a function using loaded data, e.g., ``train(Acquire, data, annotations, <other parameters>)``.

test
^^^^^^

It tests a function using loaded data, e.g., ``test(Acquire, data, annotations, <other parameters>)``.

explain
^^^^^^^^

It explains why a function generates such query results for a record



Version control
-----------------

checkout
^^^^^^^^
It checkouts a particular version of a function

history
^^^^^^^^
It shows a history of modifications to a function

commit
^^^^^^^^
It saves the changes of a function

reload
^^^^^^^^
It reloads a function if it is changed remotely

merge
^^^^^^^^
It merges a locally changed function to the master

diff
^^^^^^^^
It diffs the locally changed function with the master one

