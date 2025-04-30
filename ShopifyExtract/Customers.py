import pandas as pd
import numpy as np
import logging
import shopify
from ShopifyExtract.metadata import shopify_api_key, shopify_api_password, shopify_store_url

columns = 'id,updated_at,source_name,location_id,line_items,shipping_address,payment_details,discount_allocations,tax_lines'

def extract_order():
    shopify.Order.find(status="any", fields=columns)
    pass

pd.read_csv()    