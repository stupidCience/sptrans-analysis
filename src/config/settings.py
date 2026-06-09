import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("SPTRANS_API_KEY")
BASE_URL = "https://api.olhovivo.sptrans.com.br/v2.1"
