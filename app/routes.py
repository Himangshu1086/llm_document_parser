from flask import Blueprint, request, jsonify
from app.services.document_processor import process_document
from app.services.search_service import search_documents
import os
from app.lib.interfaces.global_response import GlobalResponse
from app.lib.enums.http_status_code import HttpStatusCode

main = Blueprint('main', __name__)


'''
This is api for uploading documents and creating a search index for the uploaded documents
'''
@main.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return GlobalResponse(data=None, message="No file part", status_code=HttpStatusCode.BAD_REQUEST.value).to_dict()
    
    file = request.files['file']
    if file.filename == '':
        return GlobalResponse(data=None, message="No selected file", status_code=HttpStatusCode.BAD_REQUEST.value).to_dict()

    if file and file.filename.endswith('.pdf'):
        try:
            process_document(file)
            return GlobalResponse(data=None, message="Document processed successfully", status_code=HttpStatusCode.OK.value).to_dict()
        except Exception as e:
            return GlobalResponse(data=None, message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()
    
    return GlobalResponse(data=None, message="Invalid file type", status_code=HttpStatusCode.BAD_REQUEST.value).to_dict()


'''
This is api for searching the uploaded documents
'''
@main.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        return GlobalResponse(data=None, message="No query provided", status_code=HttpStatusCode.BAD_REQUEST.value).to_dict()

    try:
        results = search_documents(data['query'])
        return GlobalResponse(data=results, message="Search results", status_code=HttpStatusCode.OK.value).to_dict()
    except Exception as e:
            return GlobalResponse(data=None, message="An unexpected error occurred", status_code=HttpStatusCode.INTERNAL_SERVER_ERROR.value, error=e).to_dict()