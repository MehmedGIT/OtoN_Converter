# OtoN_Converter

Converter from basic OCR-D process workflow (`.txt`) to Nextflow workflow script (`.nf`)

## 1. Installation of OtoN from source
1. Clone specific tag of the repository and enter it:
```commandline
git clone -b v1.1.0 git@github.com:MehmedGIT/OtoN_Converter.git
cd OtoN_Converter
```
2. Create a new python virtual environment and activate it:
```commandline
python3 -m venv ~/venv-oton
source ~/venv-oton/bin/activate
```

3. Install OtoN converter
```commandline
pip3 install .
```

## 2. Example conversions

1. Validation of an OCR-D process workflow txt:
    ```bash
    oton validate -I ./oton/assets/workflow1.txt
    ```

2. Conversion of an OCR-D process workflow txt to Nextflow workflow script:

   2.1 Native format of the Nextflow script
    ```bash
    oton convert -I ./oton/assets/workflow1.txt -O ./oton/assets/nextflow1.nf
    ```
    2.2 Dockerized format of the Nextflow script
    ```bash
    oton convert -I ./oton/assets/workflow1.txt -O ./oton/assets/nextflow1_dockerized.nf -D
    ```

## 3. Additional requirements (Optional)

For executing the produced Nextflow scripts there are additional requirements

1. Nextflow. Check the installation guide [here](https://www.nextflow.io/docs/latest/getstarted.html). Simple installation:
```commandline
wget -qO- https://get.nextflow.io | bash
chmod +x nextflow
mv nextflow /usr/local/bin/
nextflow -v
```

2. OCR-D ALL software for running the produced Nextflow workflows. Either installed locally or having the Docker image.
    1. Installed locally - Check the installation guide [here](https://ocr-d.de/en/user_guide#virtual-environment-native-installation).
    2. Docker image - Check the guide [here](https://ocr-d.de/en/setup.html#ocrd_all-via-docker). Or simply do:
    ```bash
    docker pull ocrd/all:maximum
    ```

## 4. Required configurations

Before proceeding to the next step `5. Example demo` there are few requirements that need to be fulfilled:

4.1 Case: OCR-D installed natively

Make sure the OCR-D processors are callable from the shell. 
For this, the `bin` path of the python virtual environment where the OCR-D all software is installed has to be available in `PATH`.
There are many ways to achieve that, but the suggested way is to extend the `$PATH` inside the `~/.profile`, `~/.bash_profile`, or `~/.bash_login`.

For example, if the path to bin is: `$HOME/venv37-ocrd/bin`. Append the following lines to either of the 3 files above.

```bash
if [ -d "$HOME/venv37-ocrd/bin" ] ; then
    PATH="$HOME/venv37-ocrd/bin:$PATH"
fi
```


4.2 Case: OCR-D docker image:

4.2.1 Download/Prepare OCR-D models to volume map them to the desired location on your system:

For example, `/home/mm/ocrd_models`.

```bash
docker run --rm -v "/home/mm/ocrd_models/:/usr/local/share/ocrd-resources" -- ocrd/all:maximum ocrd resmgr download '*'
docker run --rm -v "/home/mm/ocrd_models/:/usr/local/share/" -- ocrd/all:maximum ocrd resmgr download ocrd-tesserocr-recognize '*'
```

The selected path has to be passed as an argument to the Nextflow script. 
Check `6. Nextflow script parameters`. 
Also check the Nextflow script example with passed docker parameters [here](https://github.com/MehmedGIT/OtoN_Converter/blob/master/run_nextflow_docker.sh).

## 5. Example demo

1. Prepare the dummy workspace and workflow assets:
```bash
./prepare.sh
```
2. Run either of the available examples:

    2.1 Run the native example `(requires Nextflow and OCR-D all local installation)`

    ```bash
    ./run_nextflow_native.sh
    ```
    The Nextflow script executes native calls to the specified OCR-D processors

    2.2 Run the docker example `(requires Nextflow and OCR-D all docker image)`
    ```bash
    ./run_nextflow_docker.sh
    ```
    The Nextflow script executes docker calls to the specified OCR-D processors

3. Clean the produced files
```bash
./clean.sh
```

Currently, there are no known issues or bugs. Please report in case you find some.

## 6. Nextflow script parameters

- `mets_path`: the path to the `mets` file of an ocrd workspace.
- `workspace_path`: the workspace in which a workflow is executed.
- `docker_pwd`: the working directory of the Docker container. 
Has to match with the `workspace_path`
- `docker_image`: the docker image of `ocrd_all`. Preferably should be `ocrd/all:maximum`.
- `models_path`: the path to the models on your system.
- `docker_models_dir`: the directory to which the models are mounted in the `ocrd_all` docker container. This value usually is `"/usr/local/share/ocrd-resources"`. However, some processors (e.g., ocrd-tesserocr-recognize) may not respect that path. For more information regarding the models check [here](https://ocr-d.de/en/models).

Pass these parameters according to your needs when executing the Nextflow scripts.

Check the native call example with parameters [here](https://github.com/MehmedGIT/OtoN_Converter/blob/master/run_nextflow_native.sh).

Check the docker call example with parameters [here](https://github.com/MehmedGIT/OtoN_Converter/blob/master/run_nextflow_docker.sh).

## 7. Planned extensions

5.1. Support options to ocrd processes (i.e., the first line of the OCR-D process workflow txt) (Check [here](https://github.com/MehmedGIT/OtoN_Converter/issues/3))

5.2. Support Singularity calls inside the HPC environment - since Docker containers cannot be executed inside the HPC environment, the Docker containers have to be wrapped by Singularity containers.
