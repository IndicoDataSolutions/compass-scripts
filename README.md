Compass POC Scripts
===================

Scripts to generate indico output for Compass Packets

Setup
----

1. `git clone git@github.com:IndicoDataSolutions/compass-scripts.git`
2. `pip install -r requirements.txt`
3. set `API_TOKEN_PATH` in `config.py`
4. `python3 packet_analysis_workflow.py /path/to/packets`

Results will be found in `/path/to/packets/results`

Please note that these scripts were created as a proof of concept and 
is split into parts for understandability. It is recommended to only have
~4-5 documents in the packets directory.

Create a page text csv
-----

1. `python3 doc_extraction.py /path/to/documents` 
2. `python3 generate_text_csv.py /path/to/ocr` 

The above creates a directory named `ocr` in the `/path/to/documents` which will
contain all of the digitizations of the documents. The resulting csv will have the
following columns ( Filename, Page Number, Page Text). Note you will need to add
your own mapping for classes.