import os
from docx import Document
from docx.shared import Pt

def apply_formatting(paragraph):
    if "<h2>" in paragraph.text:
        paragraph.runs[0].bold = True
        paragraph.runs[0].font.size = Pt(13)
    elif "<h3>" in paragraph.text:
        paragraph.runs[0].bold = True
        paragraph.runs[0].font.size = Pt(12)
    else:
        paragraph.runs[0].bold = False
        paragraph.runs[0].font.size = Pt(11)

def process_word_file(input_path, output_path):
    doc = Document(input_path)
    for i, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip():
            if i == 0:
                paragraph.runs[0].bold = True
                paragraph.runs[0].font.size = Pt(14)
            else:
                apply_formatting(paragraph)

    output_file = os.path.join(output_path, os.path.basename(input_path))
    doc.save(output_file)

def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".docx"):
            input_path = os.path.join(input_folder, filename)
            process_word_file(input_path, output_folder)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: formatter.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    main(input_folder, output_folder)
