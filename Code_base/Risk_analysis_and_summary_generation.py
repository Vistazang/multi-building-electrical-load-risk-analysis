import pandas as pd
import numpy as np

from pathlib import Path

raw_data_path = Path(__file__).parent.parent/ "data" / "simulated_raw_load_data.csv"

#Raw_data_process
df=pd.read_csv(raw_data_path)

#initial_data_process
df["power_kw"]=(df["current_A"]*df["voltage_V"]/1000).round(2)
df["load_percent"]=(df["power_kw"]/df["capacity_kw"]*100).round(2)
df["capacity_margin_kw"]=(df["capacity_kw"]-df["power_kw"]).round(2)

#divide to different groups according to asset name
df = df.sort_values(["building_id", "asset_id", "timestamp"])

#ensure timestamps are sorted
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(
    ["building_id", "asset_id", "timestamp"]
).reset_index(drop=True)

#load_percent_change is the difference between the
#percentage of present load percent and one hour before

df["load_change_percent"] = (
    df.groupby(["building_id", "asset_id"])["load_percent"]
      .diff()
      .fillna(0)
      .round(2)
)
#sustained_high_load_analysis
df = df.sort_values(["building_id", "asset_id", "timestamp"])

grouped_load = df.groupby(["building_id", "asset_id"])["load_percent"]

rolling_min_3h = grouped_load.transform(
    lambda x: x.rolling(window=3, min_periods=3).min()
)

df["sustained_high_load_flag"] = (rolling_min_3h >= 85).fillna(False)

#Risk_analysis
#parameter:one row in the dataframe
#return:risk score,risk type and risk reason
#in a new three-column-dataframe

def risk_analysis(row):
    risk_score = 0
    risk_reason = []
    risk_level=""
    
    if row["load_percent"] >= 95:
        risk_score += 2
        risk_reason.append("Near or above capacity")
    elif row["load_percent"] >= 80:
        risk_score += 1
        risk_reason.append("High load")
        
    if row["capacity_margin_kw"] < 0.5:
        risk_score += 2
        risk_reason.append("Critical capacity margin")
    elif row["capacity_margin_kw"] < 2:
        risk_score += 1
        risk_reason.append("Small capacity margin")
        
    if row["load_change_percent"] > 30:
        risk_score += 2.5
        risk_reason.append("Severe load increase")
    elif row["load_change_percent"] > 20:
        risk_score += 1.5
        risk_reason.append("Rapid load increase")

    if row["sustained_high_load_flag"] == True:
        risk_score += 2
        risk_reason.append("Sustained high load")
        
    if len(risk_reason) == 0:
        risk_reason.append("No major risk found")
#Risk_level_judgement
        
    if risk_score <= 1:
        risk_level = "Normal"
    elif risk_score <= 3:
        risk_level = "Warning"
    else:
        risk_level = "High Risk"
    
#create 3 columns series for function return
    return pd.Series({"risk_score":risk_score,
                      "risk_level":risk_level,
                      "risk_reasons":risk_reason
                        })

Risk_results = df.apply(risk_analysis,axis = 1)
df = pd.concat([df,Risk_results],axis = 1)

risk_df=df[df["risk_level"]!= "Normal"]
#print(risk_df[[
#    "timestamp",
 #   "asset_id",
  #  "risk_score",
   # "risk_level",
    #"risk_reasons"
#]].head(15).to_string(index=False))   

#output path
risk_analysed_data_path = Path(__file__).parent.parent/ "data" / "risk_analysed_data.csv"
df.to_csv(risk_analysed_data_path,index=False)

