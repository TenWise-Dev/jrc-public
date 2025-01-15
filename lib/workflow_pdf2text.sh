: '
 
***************************************
Workflow for extracting text from pdfs
***************************************
 
This script is used to first load pdf files available for PMIDS, and then parse them to extract text.
Currently this only includes the material and methods section.

USAGE ::
 
    workflow_pdf2text.sh <json_file> <workdir> <repodir>
 
'
 
### END_OF_DOCSTRING ###

#!/usr/bin/bash

# ARGUMENTS
json_file=$1
workdir=$2
repodir=$3

# Directories
scriptdir=$repodir"/lib/"
output_file="$workdir/pmid_pdfs.txt"
pdfdir=$workdir"/pdfs/"
teidir=$workdir"/tei/"
textdir=$workdir"/texts/"

# Check if all the directories files exist
for dir in $workdir $repodir $scriptdir $pdfdir $teidir $textdir; do
    if [ ! -d "$dir" ]; then
        echo "Could not find directory: $dir"
        exit 1
    fi
done

# Check if the required files exist
for file in $json_file; do
    if [ ! -f "$file" ]; then
        echo "Could not find database file: $file"
        exit 1
    fi
done

# Process the database file with the Database2PDF.py script
echo " PDF EXTRACTION"
echo "================================="
if [ -f $output_file ]; then
    echo "Skipping extraction of pdfs since $output_file already exists"
else
    python3 "$scriptdir"Database2PDF.py \
                    -j $json_file \
                    -o $output_file
fi
echo "================================="
echo ""

# Load the resulting file
echo " PDF LOADING"
echo "================================="

# Use wget to download the pdfs from the urls in the tab-delimited file
while read pmid url; do
    pdf_file="$pdfdir$pmid.pdf"

    echo "Processing $pmid"
    echo "---------------------------------"
    echo "URL: $url"

    if [ -f $pdf_file ]; then
        echo ""
        echo "Skipping download of $pdf_file since it already exists"
    else
        echo ""
        echo "Downloading $pmid.pdf"
        wget -O $pdf_file $url
        echo ""

        # If resulting file has size 0KB, remove it
        if [ ! -s $pdf_file ]; then
            echo "Removing $pdf_file since its an empty file"
            rm $pdf_file
        fi

    fi
    echo ""
done < $output_file
echo "================================="
echo ""

# Use the PDF2Tei.py file to process the pdf folder
echo " PDF PROCESSING"
echo "================================="
python3 "$scriptdir"PDF2Tei.py \
                --folder $pdfdir \
                --output_folder $teidir \
                -v
echo "================================="
echo ""

# Use the Tei2MaterialMethods.py file to extract the material and methods section
echo " TEXT EXTRACTION"
echo "================================="
python3 "$scriptdir"Tei2MaterialsMethods.py \
                --tei_folder $teidir \
                --output_folder $textdir \
                -v
echo "================================="
echo ""