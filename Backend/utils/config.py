from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30")) #everything in .env exists as text so convert it into integer
#if can't find ACCESS_TOKEN_EXPIRE_MINUTES in .env, then default value is 30

GEMINI_KEY = 'AQ.Ab8RN6LH_rES4O5VjBCFFDEfUsVt4TH2Ef5kUQwM4HD1m_NITw'  # Load the Gemini API key from environment variables
