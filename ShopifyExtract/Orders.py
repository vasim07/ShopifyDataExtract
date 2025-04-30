import pandas as pd
import numpy as np
import os
import shopify
import logging
import typing
from .metadata import start_date, end_date, shopify_store_url, shopify_api_key, shopify_api_password

shopify.ShopifyResource.set_site(shopify_store_url)
shopify.ShopifyResource.set_user(shopify_api_key)  #API_KEY
shopify.ShopifyResource.set_password(shopify_api_password) #API_TOKEN

def extract_orders() -> shopify.collection.PaginatedCollection:
    all_orders = []
    #columns = 'id,updated_at,source_name,location_id,shipping_address,fulfillments,line_items,discount_allocations,tax_lines'
    orderspage = shopify.Order.find(updated_at_min= start_date, updated_at_max=end_date, status="any", limit=250)
    all_orders.extend(orderspage)
    while orderspage.has_next_page():
        orderspage = orderspage.next_page()
        all_orders.extend(orderspage)
    return all_orders

# Store json file as Bronze data.

def process_fulfillments(anorder) -> pd.DataFrame:
    # Shipped
    report_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    shipped_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['fulfillments', 'line_items'],
                      meta=['id', 'source_name', 'location_id',['fulfillments', 'updated_at']],
                      record_prefix = 'sh_',
                      errors='ignore'
                      )
    if len(shipped_items) > 0:
        shipped = shipped_items[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_gift_card', 'sh_id', 
                'sh_fulfillment_status', 'sh_price', 'sh_sku', 'sh_quantity', 'sh_pre_tax_price']]
    # Discounts
        discount_items = pd.json_normalize(anorder.to_dict(), 
                        record_path=['fulfillments', 'line_items', 'discount_allocations'],
                        meta=[['fulfillments', 'line_items', 'id']],
                        record_prefix = 'sh_',
                        errors='ignore'
                        )
        if len(discount_items)> 0:
            discount_items.loc[:,'sh_amount'] = pd.to_numeric(discount_items["sh_amount"])
            discounts = discount_items.groupby(['fulfillments.line_items.id'])['sh_amount'].sum().reset_index().set_axis(['sh_id', 'discount'], axis=1)
            shipped = pd.merge(shipped, discounts, on='sh_id', how='left')
        else:
            shipped.loc[:,'discount'] = 0
        # Taxes
        tax_items = pd.json_normalize(anorder.to_dict(), 
                        record_path=['fulfillments', 'line_items', 'tax_lines'],
                        meta=[['fulfillments', 'line_items', 'id']],
                        record_prefix = 'sh_',
                        errors='ignore'
                        )
        if len(tax_items) > 0:
            tax_items.loc[:,'tax_price'] = pd.to_numeric(tax_items["sh_price"])
            taxes = tax_items.groupby(['fulfillments.line_items.id'])['tax_price'].sum().reset_index().set_axis(['sh_id', 'tax'], axis=1)
            shipped = pd.merge(shipped, taxes, on='sh_id', how='left')
        else:
            shipped.loc[:,'tax'] = 0
        shipped = shipped[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_fulfillment_status','sh_sku', 'sh_quantity', 'sh_price', 'sh_pre_tax_price', 'sh_gift_card', 'discount', 'tax']]
        shipped = shipped.set_axis(['ORDER_ID', 'UPDATED_DATE', 'SOURCE', 'LOCATION', 'FULFILLMENT_STATUS' ,'SKU', 'QUANTITY', 'RETAIL_PRICE', 'SALES_PRICE', 'GIFT_CARD', 'DISCOUNT', 'TAX'], axis=1)
        # filter fulfillment_status, filter Updated_Date
        shipped.loc[:, 'UPDATED_DATE'] = pd.to_datetime(shipped["UPDATED_DATE"]).dt.date
        shipped["CHANNEL"] = np.where(shipped.Source_Name=='pos', "RETAIL", "ECOMMERCE")
        #shipped.query('UPDATED_DATE == @report_date')
        shipped = shipped.replace({np.nan:None})
        return shipped 
    else:
        pass

def process_refunds(anorder) -> pd.DataFrame:
    # anorder = a[2502]
    # [(k, i.to_dict()["id"]) for k,i in enumerate(a) if len(i.to_dict()["refunds"]) > 0]
    refund_items = pd.json_normalize(anorder.to_dict(), 
                      record_path=['refunds', 'refund_line_items'],
                      meta=['id', 'source_name', 'location_id',['refunds', 'updated_at']],
                      record_prefix = 'r_',
                      errors='ignore'
                      )
    # FIX
    refund_items[['id', 'fulfillments.updated_at', 'source_name', 'location_id', 'sh_fulfillment_status','sh_sku', 'sh_quantity', 'sh_price', 'sh_pre_tax_price', 'sh_gift_card', 'discount', 'tax']]
    pass
    
a = extract_orders()
dfs = [process_fulfillments(a[i]) for i in range(len(a))]
df = pd.concat(dfs)


#shopify.ShopifyResource.clear_session()