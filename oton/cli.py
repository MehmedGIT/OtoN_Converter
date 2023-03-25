import click
from pkg_resources import resource_filename
from .converter import Converter
from .validators.ocrd_validator import OCRDValidator
from .validators.validator_utils import validate_file_path
from .utils import (
    extract_file_lines,
    extract_ocrd_tokens
)


@click.group()
def cli():
    pass


default_input = resource_filename(__name__, 'assets/workflow1.txt')
default_output = resource_filename(__name__, 'assets/nextflow1.nf')


@cli.command("convert", help="Convert an OCR-D workflow to a Nextflow workflow script.")
@click.option('-I', '--input_path',
              type=click.Path(dir_okay=False, exists=True, readable=True),
              default=default_input,
              show_default=True,
              help='Path to the OCR-D workflow file to be converted.')
@click.option('-O', '--output_path',
              type=click.Path(dir_okay=False, writable=True),
              default=default_output,
              show_default=True,
              help='Path of the Nextflow workflow script to be generated.')
@click.option('-D', '--dockerized',
              is_flag=True,
              help='If set, then the dockerized variant of the Nextflow script is generated.')
def convert(input_path: str, output_path: str, dockerized: bool):
    print(f"Converting from: {input_path}")
    print(f"Converting to: {output_path}")
    Converter().convert_OtoN(input_path, output_path, dockerized)
    print("Conversion was successful!")


@cli.command("validate", help="Validate an OCR-D workflow txt file.")
@click.option('-I', '--input_path',
              default=default_input,
              show_default=True,
              help='Path to the OCR-D workflow file to be validated.')
def validate(input_path: str):
    validate_file_path(input_path)
    file_lines = extract_file_lines(input_path)
    ocrd_lines = extract_ocrd_tokens(file_lines)
    OCRDValidator().validate_ocrd_lines(ocrd_lines)
    print(f"Validating: {input_path}")
    print("Validation was successful!")
