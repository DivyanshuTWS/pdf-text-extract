import os
from pdf2image import convert_from_path

# Set the path to the directory containing PDFs
pdf_folder = r"C:\Users\divya\Downloads\box6"

# Set the path to the output directory where images will be saved
output_folder = r'D:\pdf-text-extract\box6i'

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
            # Convert the first page of the PDF into an image
            images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=1, last_page=1)
            
            # Save the first page as an image
            image_name = f"{os.path.splitext(pdf_file)[0]}_page_1.png"
            image_path = os.path.join(output_folder, image_name)
            images[0].save(image_path, 'PNG')
            
            print(f"Converted first page of {pdf_file} to image in {output_folder}")
        
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
