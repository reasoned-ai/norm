Applications
====================================

Norm targets a General Artificial Intelligence (GAI) setting, where the world is completely open. Functions declared,
implemented and trained with a subset of data, but generalized to all data. A particular usage pattern is that a user
comes with a private dataset, Norm provides an open knowledgebase with their corresponding database. User declares and
implements a model for the private dataset with functions from the openly shared knowledgebase, and test performance.
User can also utilize open database to generate auxiliary data for the task through semi-supervised learning or distant-
supervision. The function to be built might already exist in Norm open domain. The problem reduces to a customization
process for the function. If the publicly defined function does not perform well on the private dataset, the private
function will branch out its own logic implementation.

After modeling session, a new private function is built with a certain performance target. User can choose
to share the private function or keep it private.

Norm provides more resilient workflows for user to achieve the above modeling process and open up more interesting
application scenarios.


Few Shot Learning
-----------------------
As in the overview, few-shot-learning scenario allows end-user to teach a robot to understand particular concepts.


Interactive Theorem Proving
----------------------------
Model debugging process under the logic programming setting essentially is an interactive theorem proving process.


Knowledge Management
---------------------
Norm is also a good vehicle towards machine reading. With a good parser in front, a natural language statement can be
compiled to a logical program. This enables an end-to-end knowledge base construction process that maximizes the overall
prediction capability for the high level relations.


Open Domain QA
---------------
Open domain QA allows the answers constructed from open data instead of a close dataset.