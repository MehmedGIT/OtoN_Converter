# OtoN_Converter
Converter from basic OCRD process workflow to Nextflow workflow script

Usage: `python3 converter.py -i workflow1.txt -o nextflow1.nf`

Steps:
1. Convert an ocr-d workflow file to a nextflow file: `python3 converter.py -i workflow1.txt -o nextflow1.nf`  
2. Create a test workspace: `./prepare_workspace.sh`
3. Execute the nextflow script: `nextflow run nextflow1.nf` 

Currently, there are no known issues or bugs! Please report in case you find an issue.
