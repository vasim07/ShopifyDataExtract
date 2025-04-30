import pandas as pd
import numpy as np
import os
import shopify
import logging
import pandera
import typing
from .metadata import start_date, end_date, shopify_store_url, shopify_api_key, shopify_api_password

columns = 'id,updated_at,source_name,location_id,shipping_address,fulfillments,line_items,discount_allocations,tax_lines'

def extract_orders() -> shopify.collection.PaginatedCollection:
    all_orders = []
    orderspage = shopify.Order.find(updated_at_min= start_date, updated_at_max=end_date, status="any", fields=columns, limit=250)
    all_orders.extend(orderspage)
    while orderspage.has_next_page():
        orderspage = orderspage.next_page()
        all_orders.extend(orderspage)
    return all_orders

def convert_to_dataframe(anorder) -> pd.DataFrame:
    fulfilled_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['fulfillments', 'line_items'],
                      meta=['id', 'source_name', 'location_id',['fulfillments', 'updated_at']],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    fulfilled_items[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_gift_card', 'sh_id', 
                'sh_fulfillment_status', 'sh_price', 'sh_sku', 'sh_quantity', 'sh_pre_tax_price']]
    
    discount_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['line_items', 'discount_allocations'],
                      meta=['id', 'updated_at', 'source_name', 'location_id'],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    tax_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['line_items', 'tax_lines'],
                      meta=['id', 'updated_at', 'source_name', 'location_id'],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    pass



shopify.ShopifyResource.set_site(shopify_store_url)
shopify.ShopifyResource.set_user(shopify_api_key)  #API_KEY
shopify.ShopifyResource.set_password(shopify_api_password) #API_TOKEN
#shopify.ShopifyResource.clear_session()