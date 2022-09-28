# OtoN_Converter
Converter from basic OCR-D process workflow to Nextflow workflow script

### 1. Requirements:
1.1. Nextflow - Check the installation guide [here](https://www.nextflow.io/docs/latest/getstarted.html).

1.2. OCR-D software: Either installed locally or having the Docker image.
  
1.2.1 Installed locally - Check the installation guide [here](https://ocr-d.de/en/user_guide#virtual-environment-native-installation).
  
1.2.2 Docker image - Check the guide [here](https://ocr-d.de/en/setup.html#ocrd_all-via-docker).

### 2. Installation of OtoN: 
`pip3 install .`

### 3. Example usage:
3.1 Validation of an OCR-D process workflow txt:
`oton validate -I workflow1.txt`

3.2 Conversion of an OCR-D process workflow txt to Nextflow workflow script:

3.2.1 Normal conversion - if you have the OCR-D software installed locally
`oton convert -I workflow1.txt -O nextflow1.nf`

3.2.2 Dockerized conversion - if you have the OCR-D software docker image (preferably ocrd/all:maximum)
`oton convert -I workflow1.txt -O nextflow1_dockerized.nf -D`

### 4. Steps:
4.1. Validate the OCR-D workflow txt you want to convert (you can also skip this step since validation is also done on step 2 automatically)

4.2. Convert an OCR-D workflow txt file to a Nextflow workflow script (3.2.1 or 3.2.2 based on your case)

4.3. Create a test OCR-D workspace: `./prepare_workspace.sh`

4.4. Execute the Nextflow workflow script: `nextflow run nextflow1.nf` 

Currently, there are no known issues or bugs. Please report in case you find an issue.

### 5. Planned extensions:
5.1. Support options to ocrd processes (i.e., the first line of the OCR-D process workflow txt) (Check [here](https://github.com/MehmedGIT/OtoN_Converter/issues/3))

5.2. Support OCR-D Docker calls inside the HPC environment - since Docker containers cannot be executed inside the HPC environment, the Docker containers have to be wrapped by Singularity containers. 

