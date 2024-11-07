Full text analysis
==================

Setup GROBID
-------------

For transforming PDF files into XML format(more precisely TEI XML), the Grobid tool is used. There are multiple ways to setup this tool, the easiest one being using Docker.
Assuming that docker is installed in the system, this command can be used to start the GROBID server on port 8081: ::
    
        docker run --rm --init --ulimit core=0 -p 8081:8070 lfoppiano/grobid:0.8.0

The port can be changed to any other port if needed (by changing the first port number in the command).
The GROBID server can then be accessed at http://localhost:8081. All the following commands will use this port as a default.
More detailed information about Grobid in docker can be found in the `GROBID documentation <https://grobid.readthedocs.io/en/latest/Grobid-docker/>`_.

Creating TEI files from PDFs
-------------------------------

All files that are to be transformed should be placed in the same folder. There is a script in the lib folder that will take all the files from this folder and
create Tei files from them. This script can be called from the command line from the top-level folder: ::

        python3 lib/PDF2Tei.py --folder folder_with_pdfs --output_folder tei_output_folder

Optionally you can use -v to print verbose output or --port to change the port(default is 8081). ::
        
            python3 lib/PDF2Tei.py --folder folder_with_pdfs --output_folder tei_output_folder --port 8081 -v

This may take some time. If -v is used, progress will be reported after every processed file.
Grobid uses 10 threads by default and so does the script.

Extracting Materials and Method section
----------------------------------------

This script can take the folder with TEI files created in the previous step and extract the materials and methods section from each file.
It can again be called from the top-level folder.::

        python3 lib/Tei2MaterialsMethods.py --tei_folder teis_test --output_folder teis_test

The output names of the files will be the same as the original ones.
There is again -v option that will report the end of processing of each file.


Resulting JSON files
----------------------

Result of this procedure is one JSON file for every input PDF file.
The JSON file will have the following structure: ::

        {
        "Materials and Methods": [
                {
                "h1": "Materials and methods",
                "content": []
                },
                {
                "h2": "Mice",
                "content": [
                        { "p": "C57BL/6 mice (referred to as wild-type (WT) mice) were purchased from Taconic Denmark..."},
                        {"p": "A total of 40 WT, 205 F28tg, and 10 Snca KO mice were used for in vivo experiments. For experiments..."}
                ]
                },
                {
                "h2": "Pre-Formed Fibrils",
                "content": [
                        {"p": "Human \u03b1Syn (uniprot ID: P37840) was expressed in a HEK293 6E cell line and captured on an anion-exchange..."}
                ]
                },
        ]
        }

There is always header tag with the title of the section and a list of paragraphs that are in the section.
If Grobid does not recognize the hierarchy of headers, all of them will be on the same level (use h tag). 
If there are no paragraphs (e.g two headers below each other), the content will be an empty list.

If there is no Materials and Methods section in the PDF, the JSON file will be only: ::

        {
        "Materials and Methods": []
        }

