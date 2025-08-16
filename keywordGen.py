import pandas as pd
import numpy as np
import io

def campaign_keyword_template_generator(campaign_idx):
   campaign_name = campaign_idx["campaign_name"]  
   ad_group_name = campaign_idx["ad_group_name"] 
   start_date = campaign_idx["start_date"]
   targeting_type = campaign_idx["targeting_type"]
   daily_budget = campaign_idx["daily_budget"]
   asin = campaign_idx["asin"] 
   sku = campaign_idx["sku"]
   ad_group_default_bid_value = campaign_idx["ad_group_default_bid"]
   keyword_text = campaign_idx["keyword_text"]
   match_type = campaign_idx["match_type"]
   bidding_strategy = campaign_idx["bidding_strategy"]

   # SKU
   sku = pd.unique(np.char.strip(np.array(sku.split(","))))
   sku_len = len(sku)

   # ASIN
   asin = pd.unique(np.char.strip(np.array(asin.split(","))))
   asin_len = len(asin)

   # Keywords
   keyword_text = pd.unique(np.char.strip(np.array(keyword_text.split(","))))
   keyword_text_len = len(keyword_text)

   # Entities
   entity_vector = np.concatenate([
       np.array(["Ad Group"]),
       np.repeat(["Product Ad"], sku_len),
       np.repeat(["Keyword"], keyword_text_len)
   ])
   entity_vector_len = len(entity_vector)

   # Match type
   match_type = np.char.lower(np.char.strip(np.array(match_type.split(","))))
   match_type_len = len(match_type)

   # Columns
   entity_col = np.tile(entity_vector, match_type_len)
   entity_col_len = len(entity_col)
   product_col = np.repeat("Sponsored Products", entity_col_len)
   operation_col = np.repeat("Create", entity_col_len)
   campaign_col = np.repeat(campaign_name, entity_col_len)

   # Ad Group IDs
   ad_group_id_name = [ad_group_name + " " + m.capitalize() for m in match_type]
   ad_group_id_col = np.repeat(ad_group_id_name, entity_vector_len)

   # Initial DF
   campaign_df = pd.DataFrame({
       "product": product_col,
       "entity": entity_col,
       "operation": operation_col,
       "campaign_id": campaign_col,
       "ad_group_id": ad_group_id_col
   })

   campaign_df["state"] = "enabled"
   for col in ["portfolio_id","ad_id_ro","keyword_id_ro","product_targeting_id_ro",
               "ad_group_default_bid","bid","match_type","asin","sku","keyword_text",
               "ad_group_name","campaign_name","start_date","end_date","targeting_type",
               "bidding_strategy","daily_budget"]:
       campaign_df[col] = None

   # Assign values
   agdb_idx = campaign_df[campaign_df["entity"] == "Ad Group"].index
   campaign_df.loc[agdb_idx, "ad_group_default_bid"] = ad_group_default_bid_value

   bid_idx = campaign_df[campaign_df["entity"] == "Keyword"].index
   campaign_df.loc[bid_idx, "bid"] = ad_group_default_bid_value

   i = 0
   for adgi_value in campaign_df["ad_group_id"].unique():
       idxs = campaign_df[(campaign_df["entity"]=="Keyword") & (campaign_df["ad_group_id"]==adgi_value)].index
       campaign_df.loc[idxs, "match_type"] = match_type[i]
       i += 1

   for j, idx in enumerate(campaign_df[campaign_df["entity"]=="Product Ad"].index):
       campaign_df.loc[idx, "sku"] = sku[j % sku_len]
       campaign_df.loc[idx, "asin"] = asin[j % asin_len]

   for k, idx in enumerate(campaign_df[campaign_df["entity"]=="Keyword"].index):
       campaign_df.loc[idx, "keyword_text"] = keyword_text[k % keyword_text_len]

   for l, idx in enumerate(campaign_df[campaign_df["entity"]=="Ad Group"].index):
       campaign_df.loc[idx, "ad_group_name"] = campaign_name + " " + match_type[l % match_type_len].capitalize()

   # Top row
   top_row = {
       "product": "Sponsored Products", "entity":"Campaign", "operation":"Create",
       "campaign_id":campaign_name, "ad_group_id":None, "portfolio_id":None, 
       "ad_id_ro":None, "keyword_id_ro":None, "product_targeting_id_ro":None,
       "campaign_name":campaign_name, "ad_group_name":None, "start_date":start_date, 
       "end_date":None, "targeting_type":targeting_type, "state":"enabled",
       "daily_budget":daily_budget, "asin":None, "sku":None, 
       "ad_group_default_bid":None, "bid":None, "keyword_text":None, 
       "match_type":None, "bidding_strategy":bidding_strategy
   }
   top_df = pd.DataFrame(top_row, index=[0])

   campaign_df_final = pd.concat([top_df, campaign_df]).reset_index(drop=True)

   cols = ["product", "entity", "operation","campaign_id", "ad_group_id", "portfolio_id", 
           "ad_id_ro", "keyword_id_ro", "product_targeting_id_ro","campaign_name", 
           "ad_group_name", "start_date", "end_date", "targeting_type", "state",
           "daily_budget", "asin", "sku", "ad_group_default_bid", "bid","keyword_text",                           
           "match_type", "bidding_strategy"]

   campaign_df_final = campaign_df_final[cols]
   campaign_df_final.columns = [
       'Product', 'Entity', 'Operation', 'Campaign Id', 'Ad Group Id',
       'Portfolio Id', 'Ad Id (Read only)', 'Keyword Id (Read only)',
       'Product Targeting Id (Read only)', 'Campaign Name', 'Ad Group Name',
       'Start Date', 'End Date', 'Targeting Type', 'State', 'Daily Budget', 'ASIN',
       'SKU', 'Ad Group Default Bid', 'Bid', 'Keyword Text', 'Match Type',
       'Bidding Strategy'
   ]
   return campaign_df_final


def read_keyword_input_file(file_bytes):
   campaigns_data = pd.read_excel(file_bytes, index_col="Campaign Index")

   cols_name = ["campaign_name", "ad_group_name", "start_date", 
                "targeting_type", "daily_budget", "asin", "sku", 
                "ad_group_default_bid","keyword_text", "match_type", "bidding_strategy"]

   campaigns_data.columns = cols_name

   campaigns_data_df = pd.DataFrame(columns=[
       'Product', 'Entity', 'Operation', 'Campaign Id', 'Ad Group Id',
       'Portfolio Id', 'Ad Id (Read only)', 'Keyword Id (Read only)',
       'Product Targeting Id (Read only)', 'Campaign Name', 'Ad Group Name',
       'Start Date', 'End Date', 'Targeting Type', 'State', 'Daily Budget', 'ASIN',
       'SKU', 'Ad Group Default Bid', 'Bid', 'Keyword Text', 'Match Type',
       'Bidding Strategy'
   ])

   for idx in campaigns_data.index:
       row_data = campaigns_data.loc[idx, :]
       df_idx = campaign_keyword_template_generator(row_data)
       campaigns_data_df = pd.concat([campaigns_data_df, df_idx])

   return campaigns_data_df