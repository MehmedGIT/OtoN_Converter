# OtoN_Converter

Converter from basic OCR-D process workflow to Nextflow workflow script

## 1. Requirements

1. Nextflow - Check the installation guide [here](https://www.nextflow.io/docs/latest/getstarted.html).

2. OCR-D software: Either installed locally or having the Docker image.

    1. Installed locally - Check the installation guide [here](https://ocr-d.de/en/user_guide#virtual-environment-native-installation).
    2. Docker image - Check the guide [here](https://ocr-d.de/en/setup.html#ocrd_all-via-docker).

## 2. Installation of OtoN

`pip3 install .`

## 3. Example usage

1. Validation of an OCR-D process workflow txt:

    ```bash
    oton validate -I ./oton/assets/workflow1.txt
    ```

2. Conversion of an OCR-D process workflow txt to Nextflow workflow script:

    1. Normal conversion - if you have the OCR-D software installed locally

        ```bash
        oton convert -I ./oton/assets/workflow1.txt -O ./oton/assets/nextflow1.nf
        ```

    2. Dockerized conversion - if you have the OCR-D software docker image (preferably ocrd/all:maximum)

        ```bash
        oton convert -I ./oton/assets/workflow1.txt -O ./oton/assets/nextflow1_dockerized.nf -D
        ```

## 4. Configuration

The configuration of the converter available at `oton/config.toml` provides the following parameters:

- `workspace_path`: the workspace in which a workflow is executed. *Note:* `$projectDir` is a NextFlow variable that is equivalent to `.`
- `mets_path`: the location of the workspace's mets.xml. *Note:* `$projectDir` is a NextFlow variable that is equivalent to `.`
- `docker_pwd`: the working directory of the Docker container
- `docker_image`: the `ocrd_all` Docker image to be used
- `docker_models_dir`: the directory to which the models are mounted in the Docker container
- `venv_path`: the path for activating your ocrd_all venv
- `models_path`: the path to the models on your system

Adjust these parameters according to your needs and reinstall the package (if necessary).

## 5. Steps

1. Validate the OCR-D workflow txt you want to convert (you can also skip this step since validation is also done on step 2 automatically)

2. Convert an OCR-D workflow txt file to a Nextflow workflow script (3.2.1 or 3.2.2 based on your case)

3. Create a test OCR-D workspace: `./prepare_workspace.sh`

4. Execute the Nextflow workflow script: `nextflow run ./oton/assets/nextflow1.nf`

Currently, there are no known issues or bugs. Please report in case you find an issue.

## 6. Planned extensions

5.1. Support options to ocrd processes (i.e., the first line of the OCR-D process workflow txt) (Check [here](https://github.com/MehmedGIT/OtoN_Converter/issues/3))

5.2. Support OCR-D Docker calls inside the HPC environment - since Docker containers cannot be executed inside the HPC environment, the Docker containers have to be wrapped by Singularity containers.
