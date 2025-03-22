    document_search/
    │
    ├── app/
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── document_processor.py
    │   │   ├── embeddings_service.py
    │   │   └── search_service.py
    │   │
    │   ├── utils/
    │   │   ├── __init__.py
    │   │   └── text_utils.py
    │   │
    │   ├── config/
    │   │   ├── __init__.py
    │   │   └── environment.py
    │   │
    │   ├── lib/
    │   │   ├── __init__.py
    │   │   ├── enums/
    │   │   │   ├── __init__.py
    │   │   │   └── http_status_code.py
    │   │   └── interfaces/
    │   │       ├── __init__.py
    │   │       └── global_error.py
    │   │
    │   └── assets/
    │       └── financial_doc.pdf
    │
    ├── instance/
    │   └── config.py
    │
    ├── tests/
    │   ├── __init__.py
    │   └── test.py
    │
    ├── uploads/
    ├── .env
    ├── develop.Dockerfile
    ├── rebuild.sh
    ├── requirements.txt
    └── run.py


This structure provides a complete Flask application for document search and summarization. Here's what each component does:
1. **run.py**: The entry point of the application

2. **app/__init__.py**: Flask application factory

3. app/config: Configuration settings

4. app/routes.py: API endpoints for upload and search

5. app/services/:
    - document_processor.py: Handles PDF processing
    - embeddings_service.py: Manages document embeddings
    - search_service.py: Handles search functionality

6. app/utils/text_utils.py: Utility functions for text processing


### .env

        OPENAI_API_KEY=your_api_key_here
        FLASK_HOST=host
        FLASK_PORT=port


## START IN DOCKER CONTAINER

- Install docker desktop
- run   :  `sudo ./rebuild.sh`


## START LOCALLY 

### Start Virtual Environment with pip

create a virtual environment : 

`python -m venv venv`

#### Start 
**For Unix/macOS**

`source venv/bin/activate`

**For Windows**

`venv\Scripts\activate`


    # For PyMuPDF dependencies
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        python3-dev \
        libmupdf-dev \
        swig

    # For faiss-cpu dependencies
    sudo apt-get install -y \
        libopenblas-dev \
        libomp-dev
    


### With conda

*Instead of building from source, let's install the pre-built wheel. For Python 3.12 on Linux, we should use conda since pip wheels aren't currently available for this Python version. The conda approach is recommended as it handles dependencies better, but either solution should work*


First, install conda if you haven't already:

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

Create and activate a new conda environment:

    conda create -n myenv python=3.12
    conda activate myenv

Install faiss-cpu using conda:

    conda install -c conda-forge faiss-cpu


### Install the requirements:
`pip install -r requirements.txt`

### Create the uploads directory:
`mkdir uploads`

### Run the application:
`python run.py`

### API DOCUMENTATION: 

The application provides two main endpoints:

#### API CURL

- POST /upload - Upload and process PDF documents

        curl --location 'http://127.0.0.1:5000/upload' \
        --form 'file=@"postman-cloud:///1f0068ef-02cb-45b0-b657-19311e929eae"'

- POST /search - Search through processed documents

        curl --location 'http://127.0.0.1:5000/search' \
        --header 'Content-Type: application/json' \
        --data '{
            "query":"What is the interest rate in 2002 ?",
            "summary_length_type":"short" // enum = ['short', 'medium' , 'long' ]
        }'