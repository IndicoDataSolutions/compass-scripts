Compass POC Scripts
===================

Scripts to generate indico output for Compass Packets

Setup
----

1. `git clone git@github.com:IndicoDataSolutions/compass-scripts.git`
2. `pip install -r requirements.txt`
3. set `API_TOKEN_PATH` in `config.py`
4. `python3 packet_analysis_workflow.py /path/to/packets`

Please note that these scripts were created as a proof of concept and 
is split into parts for understandability. It is recommended to only have
~4-5 documents in the packets directory.