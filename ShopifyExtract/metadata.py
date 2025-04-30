from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()

shopify_api_key = os.getenv("shopify_api_key")
shopify_api_password = os.getenv("shopify_api_password")
shopify_store_url = os.getenv("shopify_store_url")

start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d") + str("T00:00:00-05:00")
end_date = (datetime.today() - timedelta(days=0)).strftime("%Y-%m-%d") + str("T00:00:00-05:00")