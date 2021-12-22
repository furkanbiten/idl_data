import os
import shutil
import tqdm
from pdf2image import pdfinfo_from_path

ROOT = '/media/abiten/14TB/IDL/'
MOVE_PATH = '/media/abiten/14TB/problems/big_files'
check_file = '/media/abiten/14TB/big_files.txt'
with open(check_file, 'r') as f:
    pdfs = f.readlines()
pdfs = [p.replace('\n', '') for p in pdfs]

if not os.path.exists(MOVE_PATH):
    os.makedirs(MOVE_PATH)

for p in tqdm.tqdm(pdfs):
    pdf_path = p.split('IDL')[-1][1:]
    pdf_folder_name = pdf_path.split('/')[-2]

    src = os.path.join(ROOT, pdf_path)

    # Textract accepts until 3000 pages and if you give more than 3000 it hangs forever,
    # So, we are not taking any chances by 100 page.
    try:
        info = pdfinfo_from_path(src, userpw=None, poppler_path=None)
        if info["Pages"] >=2900:
            dest = os.path.join(MOVE_PATH, pdf_folder_name)
            shutil.move('/'.join(src.split('/')[:-1]), dest)
    except:
        pass
