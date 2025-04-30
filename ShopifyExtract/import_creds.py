from dotenv import load_dotenv
load_dotenv()

shopify_api_key = os.getenv("shopify_api_key")
shopify_api_password = os.getenv("shopify_api_password")
shopify_store_url = os.getenv("shopify_store_url")