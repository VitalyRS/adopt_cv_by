import os
from openai import OpenAI
from odf import text, teletype
from odf.opendocument import load
from odf.text import P
import dotenv

# Load API key from .env file
dotenv.load_dotenv("key.env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
print("-------", DEEPSEEK_API_KEY, "---------------")

# Initialize DeepSeek client
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Get file names from the specified folder
def get_f_names(folder):
    try:
        files = os.listdir(folder)
        file_odt, file_txt = None, None
        for f in files:
            if f.endswith(".odt"):
                file_odt = os.path.join(folder, f)
            elif f.endswith(".txt"):
                file_txt = os.path.join(folder, f)
        if file_odt and file_txt:
            return folder, file_odt, file_txt
        else:
            print("Required files (.odt and .txt) not found in the folder.")
            return None, None, None
    except Exception as e:
        print(f"Error reading directory '{folder}': {e}")
        return None, None, None

# Extract text from an .odt file
def extract_text_from_odt(file_path):
    try:
        doc = load(file_path)
        text_content = ""
        for element in doc.getElementsByType(text.P):
            text_content += teletype.extractText(element) + "\n"
        return text_content.strip()
    except Exception as e:
        print(f"Error reading .odt file: {e}")
        return None

# Read job requirements from a .txt file
def read_job_requirements(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading job requirements file: {e}")
        return None

# Create an .odt file with given content
def create_odt_file(content, output_path):
    try:
        from odf.opendocument import OpenDocumentText
        doc = OpenDocumentText()
        for line in content.split("\n"):
            p = P()
            p.addText(line)
            doc.text.addElement(p)
        doc.save(output_path)
        print(f"File saved: {output_path}")
    except Exception as e:
        print(f"Error creating .odt file: {e}")

# Call DeepSeek API with a prompt
def call_deepseek(prompt, model="deepseek-chat"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional assistant specializing in CV adaptation and cover letter writing."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return None

# Main function
def main():
    # folder, cv_path, requirements_path = get_f_names("spotlab")
    folder, cv_path, requirements_path = get_f_names(FOLDER_NAME)
    # "spotlab"

    if not folder or not cv_path or not requirements_path:
        print("Missing necessary files. Exiting.")
        return

    # Custom user notes
    user_notes = (
        "Emphasize that I was able to understand complex concepts in fMRI and EEG analysis, "
        "and as a physicist, I am familiar with unconventional signal processing methods."
    )
    language = "English"

    # Extract CV text
    cv_text = extract_text_from_odt(cv_path)
    if not cv_text:
        print("Failed to extract CV text. Exiting.")
        return

    # Read job requirements
    job_requirements = read_job_requirements(requirements_path)
    if not job_requirements:
        print("Failed to read job requirements. Exiting.")
        return

    # Create prompt for CV adaptation
    cv_prompt = f"""
I have a CV with the following content:
{cv_text}

The job description is as follows:
{job_requirements}

My specific notes for CV adaptation:
{user_notes if user_notes else "Adapt the CV professionally without extra emphasis."}

Please adapt my CV to match the job requirements, while considering my notes. Make it professional, concise, and tailored for the role.
Format the result as plain text, with sections (e.g., Work Experience, Education) clearly separated.
Target language: {language}.
"""

    # Adapt CV using DeepSeek
    adapted_cv = call_deepseek(cv_prompt)
    if not adapted_cv:
        print("Failed to adapt CV. Exiting.")
        return

    # Create prompt for cover letter
    cover_letter_prompt = f"""
Based on the following adapted CV:
{adapted_cv}

And the job requirements:
{job_requirements}

Write a professional cover letter highlighting my suitability for the role.
The letter should be concise, persuasive, and follow business correspondence standards.
Target language: {language}.
"""

    # Generate cover letter using DeepSeek
    cover_letter = call_deepseek(cover_letter_prompt)
    if not cover_letter:
        print("Failed to generate cover letter. Exiting.")
        return

    # Save adapted CV and cover letter
    output_cv_path = os.path.join(folder, f"adapted_cv_{language.lower()}.odt")
    output_letter_path = os.path.join(folder, f"cover_letter_{language.lower()}.odt")

    create_odt_file(adapted_cv, output_cv_path)
    create_odt_file(cover_letter, output_letter_path)

    # Print results to console
    print("\nAdapted CV:")
    print(adapted_cv)
    print("\nCover Letter:")
    print(cover_letter)

FOLDER_NAME="spotlab01"
if __name__ == "__main__":
    main()
