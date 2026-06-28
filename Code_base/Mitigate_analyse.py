import pandas as pd
from pathlib import Path

#i/o file path
input_path=Path(__file__).parent.parent/"data"/"risk_analysed_data.csv"
output_path=Path(__file__).parent.parent/"data"/"mitigated_data.csv"

df=pd.read_csv(input_path)

# make sure timestamp is datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# sort before using shift
df = df.sort_values(["building_id", "asset_id", "timestamp"]).reset_index(drop=True)
#mitigation percentage calculation
#parameter: one row of dataframe
#function:calculate mitigate percent according to risk level

def risk_mitigation(row):
    if row["risk_level"]=="Normal":
        return 0
        
    elif row["risk_level"]=="Warning":
        return 8

    if row["risk_level"]=="High Risk":
        
        if "Near or above capacity"in row["risk_reasons"]:
            return 15
            
        elif "Sustained high load"in row["risk_reasons"]:
            return 13

        else:
            return 10

# Step 1: original mitigation decision for current hour
df["base_mitigation_reduction_percent"] = df.apply(risk_mitigation, axis=1)

# Step 2: previous hour mitigation carry-over
df["previous_hour_reduction_percent"] = (
    df.groupby(["building_id", "asset_id"])["base_mitigation_reduction_percent"]
      .shift(1)
      .fillna(0)
)

# Step 3: final mitigation = current hour or previous-hour carry-over, whichever is larger
df["mitigation_reduction_percent"] = df[
    ["base_mitigation_reduction_percent", "previous_hour_reduction_percent"]
].max(axis=1)

# Step 4: calculate mitigated load percent
df["mitigated_load_percent"] = (
    df["load_percent"] * (1 - df["mitigation_reduction_percent"] / 100)
).round(2)

# Step 5: calculate mitigated power
df["mitigated_power_kw"] = (
    df["power_kw"] * (1 - df["mitigation_reduction_percent"] / 100)
).round(2)

# Step 6: calculate reduction amount
df["load_percent_reduction"] = (
    df["load_percent"] - df["mitigated_load_percent"]
).round(2)

df["power_reduction_kw"] = (
    df["power_kw"] - df["mitigated_power_kw"]
).round(2)

df.to_csv(output_path, index=False)

#print(df[["timestamp","asset_id","power_kw","mitigation_reduction_percent","mitigated_load_percent","reducted_power_kw"]].head(10).to_string(index=False)
#      )
