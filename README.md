# OtoN_Converter
Converter from basic OCRD process workflow to Nextflow workflow script

### 1. Requirements:
1. Nextflow - Check the installation guide [here](https://www.nextflow.io/docs/latest/getstarted.html).
2. OCR-D Software (ocrd processors to be used) installed locally - Check the installation guide [here](https://ocr-d.de/en/setup).

### 2. Usage: 
`python3 converter.py -i inputPath -o outputPath`

### 3. Steps:
1. Convert an ocr-d workflow file to a nextflow file: `python3 converter.py -i workflow1.txt -o nextflow1.nf`
2. Create a test ocr-d workspace: `./prepare_workspace.sh`
3. Execute the nextflow script: `nextflow run nextflow1.nf` 

Currently, there are no known issues or bugs! Please report in case you find an issue.

### 4. Planned extensions:
1. Support OCR-D Docker calls inside the Nextflow scripts - in order to run the produced Nextflow scripts, the OCR-D Software have to be installed locally.
2. Support OCR-D Docker calls inside the HPC environment - since Docker containers cannot be executed inside the HPC environment, the Docker containers have to be wrapped by Singularity containers. 

