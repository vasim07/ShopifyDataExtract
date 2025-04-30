import pandas as pd
import numpy as np
import os
import shopify
import logging
import pandera
import typing
from .metadata import start_date, end_date, shopify_store_url, shopify_api_key, shopify_api_password

columns = 'id,updated_at,source_name,location_id,shipping_address,line_items,discount_allocations,tax_lines'

def extract_orders() -> shopify.collection.PaginatedCollection:
    all_orders = []
    orderspage = shopify.Order.find(updated_at_min= start_date, updated_at_max=end_date, status="any", fields=columns, limit=250)
    all_orders.extend(orderspage)
    while orderspage.has_next_page():
        orderspage = orderspage.next_page()
        all_orders.extend(orderspage)
    return all_orders

def convert_to_dataframe(anorder) -> pd.DataFrame:
    line_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['line_items'],
                      meta=['id', 'updated_at', 'source_name', 'location_id'],
                      record_prefix = 'lt_',
                      errors='ignore'
                      )
    
    discount_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['line_items', 'discount_allocations'],
                      meta=['id', 'updated_at', 'source_name', 'location_id'],
                      record_prefix = 'lt_',
                      errors='ignore'
                      )
    tax_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['line_items', 'tax_lines'],
                      meta=['id', 'updated_at', 'source_name', 'location_id'],
                      record_prefix = 'lt_',
                      errors='ignore'
                      )
    pass



shopify.ShopifyResource.set_site(shopify_store_url)
shopify.ShopifyResource.set_user(shopify_api_key)  #API_KEY
shopify.ShopifyResource.set_password(shopify_api_password) #API_TOKEN
#shopify.ShopifyResource.clear_session()