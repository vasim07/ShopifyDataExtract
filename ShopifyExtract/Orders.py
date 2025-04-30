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
    # Shipped
    fulfilled_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['fulfillments', 'line_items'],
                      meta=['id', 'source_name', 'location_id',['fulfillments', 'updated_at'],['fulfillments', 'lineitems', 'id']],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    if len(fulfilled_items) > 0:
        shipped = fulfilled_items[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_gift_card', 'sh_id', 
                'sh_fulfillment_status', 'sh_price', 'sh_sku', 'sh_quantity', 'sh_pre_tax_price', 'fulfillments.lineitems.id']]
    # Discounts
    discount_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['fulfillments', 'line_items', 'discount_allocations'],
                      meta=[['fulfillments', 'line_items', 'id']],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    if len(discount_items)> 0:
        discount_items['sh_amount'] = pd.to_numeric(discount_items["sh_amount"])
        discounts = discount_items.groupby(['fulfillments.line_items.id'])['sh_amount'].sum().reset_index().set_axis(['fulfillments.lineitems.id', 'discount'], axis=1)
        shipped = pd.merge(shipped, discounts, on='fulfillments.lineitems.id', how='left')
    # Taxes
    tax_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['fulfillments', 'line_items', 'tax_lines'],
                      meta=[['fulfillments', 'line_items', 'id']],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    if len(tax_items) > 0:
        tax_items['sh_price'] = pd.to_numeric(tax_items["sh_price"])
        taxes = tax_items.groupby(['fulfillments.line_items.id'])['sh_price'].sum().reset_index().set_axis(['fulfillments.lineitems.id', 'tax'], axis=1)
        shipped = pd.merge(shipped, taxes, on='fulfillments.lineitems.id', how='left')
    #shipped = shipped[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_sku', 'sh_quantity', 'sh_price', 'sh_pre_tax_price', 'sh_gift_card', 'discount', 'tax']]
    return shipped

convert_to_dataframe(a[2847])

shopify.ShopifyResource.set_site(shopify_store_url)
shopify.ShopifyResource.set_user(shopify_api_key)  #API_KEY
shopify.ShopifyResource.set_password(shopify_api_password) #API_TOKEN
#shopify.ShopifyResource.clear_session()