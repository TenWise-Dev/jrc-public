.. warning::

    Since we are still working on this project and designing the best workflows, the scripts and their associated command line parameters are subject to change. However we expect that the overall functionality of the scripts will not change significantly. So they can be used already, but production level workflows should not yet be build on these scripts.


Scripts
=======

The scripts are supplied as standalone files, not as a packaged library. Most scripts take arguments for input and output files as command line arguments and can thus be used to redirect and retrieve data according to the specific directory set-up of your system. 


Database handling
#################




A set of scripts that deals with creation and updating the JSON formatted database. 

.. _my-query2pmid-label:

Query2PMID
----------

.. automodule:: Query2PMID



.. _my-pmid2database-label:

PMID2Database
-------------

.. automodule:: PMID2Database



.. _my-openalex-label:

PMID2Openalex
-------------

An R script used for the retrieval of OpenAlex identifiers

.. _my-pmid2tags-label:

PMID2Tags
---------

.. automodule:: PMID2Tags


DatabaseUpdate.py
------------------

.. automodule:: DatabaseUpdate

.. _my-databasemerge-label:

DatabaseMerge.py
------------------

.. automodule:: DatabaseMerge


Modelling
#########

A set of scripts that deals with creation of predictive models.

PMID2Embed.py
-------------

.. automodule:: PMID2Embed

PMID2Tfidf.py
-------------    

.. automodule:: PMID2Tfidf  


PMID2Doc2Vec.py
---------------

.. automodule:: PMID2Doc2Vec

.. _my-tagabstracts-label:


PMID2BOW.py
-----------

.. automodule:: PMID2BOW


PMID2Predict.py
---------------

.. automodule:: PMID2Predict

PMID2Model.py
-------------

.. automodule:: PMID2Model