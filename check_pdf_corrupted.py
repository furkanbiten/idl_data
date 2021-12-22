import PyPDF2
import os
import tqdm
import shutil


ROOT = '/media/abiten/14TB/IDL/'
OUT = '/media/abiten/14TB/problems/corrupted'
BUCKET_NAME = 'edu.ucsf.industrydocuments.artifacts'
root_folders = ['f', 'g', 'h', 'j', 'k']
subfolders_type1 = os.listdir(ROOT + 'f')
subfolders_type2 = os.listdir(ROOT + 'f/f')

if not os.path.exists(OUT):
    os.makedirs(OUT)

for r in root_folders:
    for s1 in subfolders_type1:
        for s2 in subfolders_type2:
            for s3 in tqdm.tqdm(subfolders_type2):
                pdf_root = os.path.join(ROOT, r, s1, s2, s3)
                for i in os.listdir(pdf_root):
                    try:
                        PyPDF2.PdfFileReader(open(os.path.join(pdf_root, i, i+'.pdf'), "rb"))
                    except Exception as e:
                        shutil.move(os.path.join(pdf_root, i), os.path.join(OUT, i))
                        print("invalid PDF file")