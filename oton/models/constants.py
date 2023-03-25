__all__ = [
    "DIR_IN",
    "DIR_OUT",
    "METS_FILE",

    "PARAMS_KEY_DOCKER_PWD",
    "PARAMS_KEY_DOCKER_VOLUME",
    "PARAMS_KEY_DOCKER_MODELS",
    "PARAMS_KEY_DOCKER_IMAGE",
    "PARAMS_KEY_DOCKER_COMMAND",
    "PARAMS_KEY_METS_PATH",
    "PARAMS_KEY_VENV_PATH",
    "PARAMS_KEY_WORKSPACE_PATH",

    "PARAMS_VAL_DOCKER_PWD",
    "PARAMS_VAL_DOCKER_VOLUME",
    "PARAMS_VAL_DOCKER_MODELS",
    "PARAMS_VAL_DOCKER_IMAGE",
    "PARAMS_VAL_DOCKER_COMMAND",
    "PARAMS_VAL_METS_PATH",
    "PARAMS_VAL_VENV_PATH",
    "PARAMS_VAL_WORKSPACE_PATH",

    "PH_DOCKER_COMMAND",
    "PH_DIR_IN",
    "PH_DIR_OUT",
    "PH_VENV_PATH",

    "REPR_DSL2",
    "REPR_DOCKER_COMMAND",
    "REPR_DOCKER_IMAGE",
    "REPR_DOCKER_MODELS",
    "REPR_DOCKER_MODELS_DIR",
    "REPR_DOCKER_PWD",
    "REPR_DOCKER_VOLUME",
    "REPR_METS_PATH",
    "REPR_MODELS_PATH",
    "REPR_VENV_PATH",
    "REPR_WORKSPACE_PATH",

]

# Parameter keys
PARAMS_KEY_DOCKER_COMMAND: str = 'params.docker_command'
PARAMS_KEY_DOCKER_IMAGE: str = 'params.docker_image'
PARAMS_KEY_DOCKER_PWD: str = 'params.docker_pwd'
PARAMS_KEY_DOCKER_VOLUME: str = 'params.docker_volume'
PARAMS_KEY_DOCKER_MODELS: str = 'params.docker_models'
PARAMS_KEY_DOCKER_MODELS_DIR: str = 'params.docker_models_dir'
PARAMS_KEY_METS_PATH: str = 'params.mets_path'
PARAMS_KEY_MODELS_PATH: str = 'params.models_path'
PARAMS_KEY_VENV_PATH: str = 'params.venv_path'
PARAMS_KEY_WORKSPACE_PATH: str = 'params.workspace_path'


def __build_docker_command():
    docker_command = 'docker run --rm'
    docker_command += f' -u \\$(id -u)'
    docker_command += f' -v ${PARAMS_KEY_DOCKER_VOLUME}'
    docker_command += f' -v ${PARAMS_KEY_DOCKER_MODELS}'
    docker_command += f' -w ${PARAMS_KEY_DOCKER_PWD}'
    docker_command += f' -- ${PARAMS_KEY_DOCKER_IMAGE}'
    return docker_command


# Parameter values
PARAMS_VAL_METS_PATH: str = "$projectDir/ocrd-workspace/mets.xml"
PARAMS_VAL_VENV_PATH: str = "\\$HOME/venv37-ocrd/bin/activate"
PARAMS_VAL_WORKSPACE_PATH: str = "$projectDir/ocrd-workspace/"
PARAMS_VAL_DOCKER_IMAGE: str = "ocrd/all:maximum"
PARAMS_VAL_DOCKER_PWD: str = "/ocrd-workspace"
PARAMS_VAL_MODELS_PATH: str = "\\$HOME/ocrd_models"
PARAMS_VAL_DOCKER_MODELS_DIR: str = "/usr/local/share/ocrd-resources"
PARAMS_VAL_DOCKER_VOLUME: str = f'${PARAMS_KEY_WORKSPACE_PATH}:${PARAMS_KEY_DOCKER_PWD}'
PARAMS_VAL_DOCKER_MODELS: str = f'${PARAMS_KEY_MODELS_PATH}:${PARAMS_KEY_DOCKER_MODELS_DIR}'
PARAMS_VAL_DOCKER_COMMAND: str = __build_docker_command()


def __build_repr(parameter, value):
    return f'{parameter} = "{value}"'


# Parameters - file representation
REPR_DSL2: str = 'nextflow.enable.dsl = 2'
REPR_DOCKER_COMMAND: str = __build_repr(PARAMS_KEY_DOCKER_COMMAND, PARAMS_VAL_DOCKER_COMMAND)
REPR_DOCKER_IMAGE: str = __build_repr(PARAMS_KEY_DOCKER_IMAGE, PARAMS_VAL_DOCKER_IMAGE)
REPR_DOCKER_MODELS: str = __build_repr(PARAMS_KEY_DOCKER_MODELS, PARAMS_VAL_DOCKER_MODELS)
REPR_DOCKER_MODELS_DIR: str = __build_repr(PARAMS_KEY_DOCKER_MODELS_DIR, PARAMS_VAL_DOCKER_MODELS_DIR)
REPR_DOCKER_PWD: str = __build_repr(PARAMS_KEY_DOCKER_PWD, PARAMS_VAL_DOCKER_PWD)
REPR_DOCKER_VOLUME: str = __build_repr(PARAMS_KEY_DOCKER_VOLUME, PARAMS_VAL_DOCKER_VOLUME)
REPR_METS_PATH: str = __build_repr(PARAMS_KEY_METS_PATH, PARAMS_VAL_METS_PATH)
REPR_MODELS_PATH: str = __build_repr(PARAMS_KEY_MODELS_PATH, PARAMS_VAL_MODELS_PATH)
REPR_VENV_PATH: str = __build_repr(PARAMS_KEY_VENV_PATH, PARAMS_VAL_VENV_PATH)
REPR_WORKSPACE_PATH: str = __build_repr(PARAMS_KEY_WORKSPACE_PATH, PARAMS_VAL_WORKSPACE_PATH)

DIR_IN: str = 'input_dir'
DIR_OUT: str = 'output_dir'
METS_FILE: str = 'mets_file'

# Placeholders
BS: str = '{}'
PH_DOCKER_COMMAND: str = f'${BS[0]}{PARAMS_KEY_DOCKER_COMMAND}{BS[1]}'
PH_DIR_IN: str = f'${BS[0]}{DIR_IN}{BS[1]}'
PH_DIR_OUT: str = f'${BS[0]}{DIR_OUT}{BS[1]}'
PH_VENV_PATH: str = f'${BS[0]}{PARAMS_KEY_VENV_PATH}{BS[1]}'
