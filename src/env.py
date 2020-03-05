import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BITFLYER_API_KEY = os.environ.get("BITFLYER_API_KEY")
BITFLYER_API_SECRET = os.environ.get("BITFLYER_API_SECRET")
