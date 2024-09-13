import openai
import csv
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API credentials from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_AZURE_ENDPOINT")
model_name = os.getenv("OPENAI_DEPLOYMENT_NAME")  

# Input and output paths
input_image_path = r'input\Drawing compressed.jpg'  # Adjust the image file name as needed
output_csv_path = r'output/output.csv'

# Define the prompt
prompt = """
The drawing contains various component or section such as "Detail of operating Plate form", 
"U/S elevation of shutter", "section elevation at A-A", "section elevation at B-B", "Details at D-D", 
"Details at X", "Details of groove". Each of the section or component has their own specifications like height 
and width, also they are having number of equipments like various type of bolts, seals, clamps, plates, 
stiffeners, and screws. 

Please provide details of each component that I mentioned along with their dimensions and the number of each 
equipment used. Note that the component name is written below the related diagram, so kindly give me related 
data above the section or component name. Also, provide 'designed by', 'submitted by', 'drawn by', 'checked by', 
'recommended by', 'traced by', and 'accepted by'. Return the values without explanation.
"""

# Function to interact with OpenAI API
def extract_metadata_from_image(image_path, prompt):
    # Load the image (currently just reading, but this can involve pre-processing if needed)
    with open(image_path, 'rb') as image_file:
        image = image_file.read()

    # Send the request to OpenAI's API using the new API format for version >=1.0.0
    response = openai.completions.create(
        model=model_name,  # Use your specific model name here
        messages=[
            {"role": "system", "content": "You are an assistant skilled in extracting metadata from engineering drawings."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=2000
    )
    
    # Extract the text from the response
    return response['choices'][0]['message']['content'].strip()

# Write metadata to CSV
def save_metadata_to_csv(metadata, output_path):
    # Assuming metadata comes in a structured form, here’s an example of saving it to a CSV
    headers = ["Component", "Dimensions", "Equipments", "Designed By", "Submitted By", "Drawn By", 
               "Checked By", "Recommended By", "Traced By", "Accepted By"]

    # For now, let's assume metadata is a dictionary where the component name is the key
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write headers
        
        for component, details in metadata.items():
            writer.writerow([component] + details)

# Main function
def main():
    # Extract metadata
    metadata = extract_metadata_from_image(input_image_path, prompt)
    
    # Save to CSV
    save_metadata_to_csv(metadata, output_csv_path)
    print(f"Metadata saved successfully in {output_csv_path}")

if __name__ == "__main__":
    main()