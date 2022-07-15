// enables a syntax extension that allows definition of module libraries
nextflow.enable.dsl = 2

// pipeline parameters
params.venv = "\$HOME/venv37-ocrd/bin/activate"
params.workspace = "$projectDir/ocrd-workspace/"
params.mets = "$projectDir/ocrd-workspace/mets.xml"

process ocrd_cis_ocropy_binarize
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-cis-ocropy-binarize -I OCR-D-IMG -O OCR-D-BIN
	 deactivate
	 """
}

process ocrd_anybaseocr_crop
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-anybaseocr-crop -I OCR-D-BIN -O OCR-D-CROP
	 deactivate
	 """
}

process ocrd_skimage_binarize
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-skimage-binarize -I OCR-D-CROP -O OCR-D-BIN2 -P method li
	 deactivate
	 """
}

process ocrd_skimage_denoise
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-skimage-denoise -I OCR-D-BIN2 -O OCR-D-BIN-DENOISE -P level-of-operation page
	 deactivate
	 """
}

process ocrd_tesserocr_deskew
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-tesserocr-deskew -I OCR-D-BIN-DENOISE -O OCR-D-BIN-DENOISE-DESKEW -P operation_level page
	 deactivate
	 """
}

process ocrd_cis_ocropy_segment
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-cis-ocropy-segment -I OCR-D-BIN-DENOISE-DESKEW -O OCR-D-SEG -P level-of-operation page
	 deactivate
	 """
}

process ocrd_cis_ocropy_dewarp
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-cis-ocropy-dewarp -I OCR-D-SEG -O OCR-D-SEG-LINE-RESEG-DEWARP
	 deactivate
	 """
}

process ocrd_calamari_recognize
{
	 maxForks 1

	 input:
	 	 path mets_file

	 script:
	 """
	 source "${params.venv}"
	 ocrd-calamari-recognize -I OCR-D-SEG-LINE-RESEG-DEWARP -O OCR-D-OCR -P checkpoint_dir qurator-gt4histocr-1.0
	 deactivate
	 """
}

workflow
{
	 main:
	 	 ocrd_cis_ocropy_binarize(params.mets)
	 	 ocrd_anybaseocr_crop(params.mets)
	 	 ocrd_skimage_binarize(params.mets)
	 	 ocrd_skimage_denoise(params.mets)
	 	 ocrd_tesserocr_deskew(params.mets)
	 	 ocrd_cis_ocropy_segment(params.mets)
	 	 ocrd_cis_ocropy_dewarp(params.mets)
	 	 ocrd_calamari_recognize(params.mets)
}
