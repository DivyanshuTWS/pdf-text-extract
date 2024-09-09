import os
from pdf2image import convert_from_path

# Set the path to the directory containing PDFs
pdf_folder = r'D:\pdf-text-extract\box010'

# Set the path to the output directory where images will be saved
output_folder = r'D:\pdf-text-extract\box10'

# Poppler path
poppler_path = r"C:\Users\divya\Downloads\Release-24.07.0-0\poppler-24.07.0\Library\bin"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop through all PDF files in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith('.pdf'):
        # Construct full path to the PDF file
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        try:
            # Convert the PDF into images (one image per page)
            images = convert_from_path(pdf_path, poppler_path=poppler_path)
            
            # Save each page as an image
            for i, image in enumerate(images):
                image_name = f"{os.path.splitext(pdf_file)[0]}_page_{i + 1}.png"
                image_path = os.path.join(output_folder, image_name)
                image.save(image_path, 'PNG')
            
            print(f"Converted {pdf_file} to images in {output_folder}")
        
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
