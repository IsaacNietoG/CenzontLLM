from unstructured.partition.pdf import partition_pdf
from pathlib import Path

def extract_elements(pdf_path: str):
    # Crear directorio de imágenes ANTES de extraer
    Path("tmp_images").mkdir(exist_ok=True)
    
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        infer_table_structure=True,
        languages=["spa", "eng"],
        extract_images_in_pdf=True,
        image_output_dir_path="tmp_images/"
    )
    return elements
