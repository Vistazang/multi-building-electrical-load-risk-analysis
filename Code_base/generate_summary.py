from pathlib import Path
import pandas as pd

base_path = Path(__file__).parent.parent

mitigated_data_path = base_path / "data" / "mitigated_data.csv"

summary_output_folder = base_path / "outputs" / "summary"
summary_output_folder.mkdir(parents=True, exist_ok=True)


#risk summary
df = pd.read_csv(mitigated_data_path)
df["timestamp"] = pd.to_datetime(df["timestamp"])

asset_risk_summary = (
    df
    .groupby(["building_id", "asset_id", "asset_type"])
    .agg(
        max_load_percent=("load_percent", "max"),
        average_load_percent=("load_percent", "mean"),
        max_power_kw=("power_kw", "max"),
        min_capacity_margin_kw=("capacity_margin_kw", "min"),
        warning_hours=("risk_level", lambda x: (x == "Warning").sum()),
        high_risk_hours=("risk_level", lambda x: (x == "High Risk").sum()),
        sustained_high_load_hours=("sustained_high_load_flag", "sum")
    )
    .reset_index()
)

asset_risk_summary = asset_risk_summary.round(2)

asset_risk_summary_path = summary_output_folder / "asset_risk_summary.csv"
asset_risk_summary.to_csv(asset_risk_summary_path, index=False)

print(f"Asset risk summary saved to: {asset_risk_summary_path}")

#mitigation summary
mitigation_summary = (
    df
    .groupby(["building_id", "asset_id", "asset_type"])
    .agg(
        max_load_before=("load_percent", "max"),
        max_load_after=("mitigated_load_percent", "max"),
        average_load_before=("load_percent", "mean"),
        average_load_after=("mitigated_load_percent", "mean"),
        total_power_reduction_kw=("power_reduction_kw", "sum"),
        average_power_reduction_kw=("power_reduction_kw", "mean"),
        max_power_reduction_kw=("power_reduction_kw", "max")
    )
    .reset_index()
)

mitigation_summary["peak_load_reduction_percent"] = (
    mitigation_summary["max_load_before"] -
    mitigation_summary["max_load_after"]
)

mitigation_summary["average_load_reduction_percent"] = (
    mitigation_summary["average_load_before"] -
    mitigation_summary["average_load_after"]
)

mitigation_summary = mitigation_summary.round(2)

mitigation_summary_path = summary_output_folder / "mitigation_summary.csv"
mitigation_summary.to_csv(mitigation_summary_path, index=False)

print(f"Mitigation summary saved to: {mitigation_summary_path}")
