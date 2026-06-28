import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

#line style directionary
line_styles = {
    "original": {
        "color": "tab:blue",
        "linewidth": 1.5,
        "linestyle": "-"
    },
    "mitigated": {
        "color": "tab:green",
        "linewidth": 1.5,
        "linestyle": "-",
        "alpha": 0.5
    },
    "warning_threshold": {
        "color": "tab:orange",
        "linewidth": 1,
        "linestyle": "--"
    },
    "high_risk_threshold": {
        "color": "tab:red",
        "linewidth": 1,
        "linestyle": "--"
    }
}
#Base directory path
base_path=Path(__file__).parent.parent
#plot output folder
plot_output_folder = base_path / "outputs" / "plots"
#plot daily and inspection folder
daily_plot_folder = plot_output_folder / "daily_max"
inspection_plot_folder = plot_output_folder / "inspection_hourly"

daily_plot_folder.mkdir(parents=True, exist_ok=True)
inspection_plot_folder.mkdir(parents=True, exist_ok=True)
#risk processed data path
risk_analysed_data_path= base_path/"data"/"risk_analysed_data.csv"
#mitigated data path
mitigated_data_path=base_path/"data"/"mitigated_data.csv"


#small amount of data ploting
def plot_hourly_asset_load(df, asset_id, output_path=None):
    plt.figure(figsize=(14, 7))
    
    df=df.sort_values("timestamp")
    x=np.array(df["timestamp"])
    y1=np.array(df["load_percent"])
    y2=np.array(df["mitigated_load_percent"])

    plt.title(f"Original vs Mitigated Load Percent - {asset_id}",
              fontsize=14,
              family="Times New Roman",
              fontweight="bold",
              pad=18
    )
    plt.xlabel("Timestamp",
               fontsize=12,
               fontweight="bold"
    )
    plt.ylabel("Original and Mitigated Load Percent",
               fontsize=12,
               fontweight="bold",
               labelpad=12
    )

    plt.plot(x,y1,**line_styles["original"],
             label="Original percent"
    )
    plt.plot(x,y2,**line_styles["mitigated"],
             label="Mitigated percent"
    )

    plt.axhline(
        80,
        **line_styles["warning_threshold"],
        label="Warning threshold 80%"
    )
    plt.axhline(
        95,
        **line_styles["high_risk_threshold"],
        label="High risk threshold 95%"
    )
    plt.xticks(rotation=45)
    
    plt.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.28),
    ncol=2,
    fontsize=10
    )
    
    plt.grid(True,alpha=0.3)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.28)

    if output_path is None:
        output_path = plot_output_folder / f"hourly_load_mitigation_{asset_id}.png"

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    pass

#certain time interval search
def search_hourly_asset_data(df, asset_id, start_date, days):
    start_time = pd.to_datetime(start_date)
    end_time = start_time + pd.Timedelta(days=days)

    inspection_df = df[
        (df["asset_id"] == asset_id) &
        (df["timestamp"] >= start_time) &
        (df["timestamp"] < end_time)
    ].copy()

    if inspection_df.empty:
        print("No data found for this asset and date range.")
        return

    output_path = (
        inspection_plot_folder
        / f"inspection_hourly_{asset_id}_{start_date}_{days}days.png"
    )

    plot_hourly_asset_load(
        inspection_df,
        asset_id,
        output_path=output_path
    )

#large amount of data ploting
def plot_daily_max_asset_load(df,asset_id):
    df = df.sort_values("timestamp")
    plt.figure(figsize=(19, 7))
    
    daily_max_df = (
    df
    .resample("D", on="timestamp")
    .agg({
        "load_percent": "max",
        "mitigated_load_percent": "max"
    })
    .reset_index()
    )

    x=np.array(daily_max_df["timestamp"])
    y1=np.array(daily_max_df["load_percent"])
    y2=np.array(daily_max_df["mitigated_load_percent"])

    plt.title(f"Daily Max Percent Original vs Mitigated Load Percent - {asset_id}",
              fontsize = 14,
              family="Times New Roman",
              fontweight="bold",
              pad=18
    )
    plt.xlabel("Timestamp",
               fontsize=12,
               fontweight="bold"
    )
    plt.ylabel("Original and Mitigated Daily Max Load Percent",
               fontsize=12,
               fontweight="bold",
               labelpad=12
    )

    plt.axhline(
        80,
        **line_styles["warning_threshold"],
        label="Warning threshold 80%"
    )
    plt.axhline(
        95,
        **line_styles["high_risk_threshold"],
        label="High risk threshold 95%"
    )
    plt.xticks(rotation=45)
    
    plt.plot(x,y1,**line_styles["original"],label="Daily max original percent")
    plt.plot(x,y2,**line_styles["mitigated"],label="Daily max mitigated percent")
    
    plt.legend()
    plot_output_path = daily_plot_folder / f"daily_max_load_mitigation_{asset_id}.png"
    plt.savefig(plot_output_path, dpi=300, bbox_inches="tight")
    plt.close()


    pass


# main function calls
after_mitigation_df = pd.read_csv(mitigated_data_path)

# adjust timestamp to support time-based plotting and filtering
after_mitigation_df["timestamp"] = pd.to_datetime(after_mitigation_df["timestamp"])


# Step 1: Generate daily max overview plots for all assets
print("\nGenerating daily max overview plots...")

for asset_id in after_mitigation_df["asset_id"].unique():
    asset_df = after_mitigation_df[
        after_mitigation_df["asset_id"] == asset_id
    ].copy()

    plot_daily_max_asset_load(asset_df, asset_id)

print("Daily max overview plots generated.")
print(f"Saved to: {daily_plot_folder}")


# Step 2: Hourly inspection search after reviewing overview plots
print("\n================ Hourly Inspection Search ================")
print("Daily max plots have been generated first.")
print("Use them to identify which asset and date range need closer inspection.\n")

print("Available asset_id options:")
for asset_id in after_mitigation_df["asset_id"].unique():
    print(f"  - {asset_id}")

print("\nInput format guide:")
print("  asset_id    : choose one from the list above")
print("  start_date  : YYYY-MM-DD, example: 2026-05-10")
print("  days        : number of days to inspect, example: 3")

print("\nExample input:")
print("  asset_id   = EV_Charger_Panel_C1")
print("  start_date = 2026-05-10")
print("  days       = 3")
print("==========================================================\n")

search_asset_id = input("Enter asset_id: ")
search_start_date = input("Enter start date YYYY-MM-DD: ")
search_days = int(input("Enter number of days: "))

search_hourly_asset_data(
    after_mitigation_df,
    search_asset_id,
    search_start_date,
    search_days
)

print("\nHourly inspection plot generated.")
print(f"Saved to: {inspection_plot_folder}")
