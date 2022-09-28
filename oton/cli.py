import click
from .converter import Converter
from .ocrd_validator import OCRD_Validator

@click.group()
def cli():
    pass

@cli.command("convert", help="Convert an OCR-D workflow to a Nextflow workflow script.")
@click.option('-I', '--input_path',
              default='./workflow1.txt',
              help='Path to the OCR-D workflow file to be converted.')
@click.option('-O', '--output_path',
              default='./nextflow1.nf',
              help='Path of the Nextflow workflow script to be generated.')
@click.option('-D', '--dockerized',
              is_flag=True,
              help='If set, then the dockerized variant of the Nextflow script is generated.')
def convert(input_path, output_path, dockerized):
    converter = Converter()
    print(f"Converting from: {input_path}")
    print(f"Converting to: {output_path}")
    converter.convert_OtoN(input_path, output_path, dockerized)
    print(f"Convertion was successful!")

@cli.command("validate", help="Validate an OCR-D workflow txt file")
@click.option('-I', '--input_path',
              default='./workflow1.txt',
              help='Path to the OCR-D workflow file to be validated.')
def validate(input_path):
    OCRD_Validator().validate_ocrd_file(input_path)
    print(f"Validating: {input_path}")
    print(f"Validation was successful!")
