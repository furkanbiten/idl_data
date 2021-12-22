import boto3
import os
import tqdm 
import time 
import json 

from botocore.client import Config
from joblib import Parallel, delayed

def dump_json(results, paths):
    path_to_save, object_name = paths[0], paths[1]
    pdf = object_name.split('/')[-1]
    json_out = os.path.join(path_to_save, pdf+'.json')
    
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
#     json_path = "{:}/{:}".format(dir_path, splitted_doc[-1].replace('.pdf', '.json'))
    json.dump(results, open(json_out, 'w'))

def get_response(response, comb, textract):
    for ix, resp in enumerate(response):

        ocr = textract.get_document_text_detection(JobId=resp['JobId'])
        while ocr['JobStatus'] != 'SUCCEEDED':
            time.sleep(1)
            ocr = textract.get_document_text_detection(JobId=resp['JobId'])
            if ocr['JobStatus'] == 'FAILED':
                print(ocr)
                break
        
        results = [comb[ix][1], ocr]
        if 'NextToken' in ocr:
            while 'NextToken' in ocr:
                ocr=textract.get_document_text_detection(JobId=resp['JobId'], NextToken=ocr['NextToken'])
                results.append(ocr)
        
        dump_json(results, comb[ix])

def run_textract(args):
    pdf_root, s3, KEYS, ix = args
    pdf_root = os.path.join(pdf_root, s3)
    print(pdf_root)
    # if os.path.exists(pdf_root.replace('IDL', 'OCR')):
    #     continue

    pdfs = [os.path.join(pdf_root, p).replace('IDL', 'OCR') for p in os.listdir(pdf_root)]
    object_names = [os.path.join(pdf_root.replace(ROOT, ''), p) for p in os.listdir(pdf_root)]

    config = Config(retries=dict(max_attempts=5))
    textract = boto3.client('textract', aws_access_key_id=KEYS[(ix+1)%len(KEYS)][0],
                            aws_secret_access_key=KEYS[(ix+1)%len(KEYS)][1],
                            region_name='us-west-2',
                           config=config)

    # for comb in tqdm.tqdm(zip(*[iter(zip(pdfs, object_names))]*MAX_ASYNC_OPS), total=len(pdfs)/MAX_ASYNC_OPS, position=ix):
    for i in tqdm.tqdm(range(len(pdfs) // MAX_ASYNC_OPS + 1), position=ix):
        response, file_names = [], []
        # for p_path, obj_name in comb:
        for p_path, obj_name in zip(pdfs[i*MAX_ASYNC_OPS:(i+1)*MAX_ASYNC_OPS],
                                    object_names[i*MAX_ASYNC_OPS:(i+1)*MAX_ASYNC_OPS]):
            if os.path.exists(p_path):
                continue
                
            pdf = p_path.split('/')[-1]
            pdf_name = os.path.join(obj_name, pdf+'.pdf')
            try:
                r = textract.start_document_text_detection(DocumentLocation={'S3Object': {'Bucket': BUCKET_NAME, 'Name': pdf_name}})
                response.append(r)
                file_names.append((p_path, obj_name))
            except Exception as e:
                print(e)
        
        if response:
            get_response(response, file_names, textract)



if __name__ == "__main__":
    
    MAX_ASYNC_OPS = 20
    ROOT = '/media/abiten/14TB/IDL/'
    BUCKET_NAME = 'edu.ucsf.industrydocuments.artifacts'
    root_folders = ['f','g', 'h', 'j', 'k']
    subfolders_type1 = os.listdir(ROOT+'f')
    subfolders_type2 = os.listdir(ROOT+'f/f')
    NUM_THREAD = 16

    KEYS = [(),()]

    for r in root_folders:
        for s1 in subfolders_type1:
            for s2 in subfolders_type2:
                pdf_root = os.path.join(ROOT, r, s1, s2)
                Parallel(n_jobs=NUM_THREAD)(delayed(run_textract)((pdf_root, s3, KEYS, ix,)) for ix, s3 in enumerate(subfolders_type2))
