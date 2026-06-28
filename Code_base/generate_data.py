import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

# -----------------------------
# 1. Asset configuration
# -----------------------------

ASSETS = [
    {
        "building_id": "Building_A",
        "asset_id": "Transformer_A1",
        "asset_type": "Transformer",
        "nominal_voltage_V": 480,
        "capacity_kw": 225
    },
    {
        "building_id": "Building_A",
        "asset_id": "Main_Panel_A1",
        "asset_type": "Main Panel",
        "nominal_voltage_V": 480,
        "capacity_kw": 150
    },
    {
        "building_id": "Building_A",
        "asset_id": "Lighting_Panel_A1",
        "asset_type": "Lighting Panel",
        "nominal_voltage_V": 208,
        "capacity_kw": 45
    },

    {
        "building_id": "Building_B",
        "asset_id": "Transformer_B1",
        "asset_type": "Transformer",
        "nominal_voltage_V": 480,
        "capacity_kw": 250
    },
    {
        "building_id": "Building_B",
        "asset_id": "Main_Panel_B1",
        "asset_type": "Main Panel",
        "nominal_voltage_V": 480,
        "capacity_kw": 160
    },
    {
        "building_id": "Building_B",
        "asset_id": "HVAC_Panel_B1",
        "asset_type": "HVAC Panel",
        "nominal_voltage_V": 480,
        "capacity_kw": 75
    },

    {
        "building_id": "Building_C",
        "asset_id": "Main_Panel_C1",
        "asset_type": "Main Panel",
        "nominal_voltage_V": 480,
        "capacity_kw": 180
    },
    {
        "building_id": "Building_C",
        "asset_id": "EV_Charger_Panel_C1",
        "asset_type": "EV Charger Panel",
        "nominal_voltage_V": 480,
        "capacity_kw": 80
    }
]


# -----------------------------
# 2. Temperature simulation
# -----------------------------

def generate_temperature(hour_of_day):
    """
    Simulate outdoor temperature.
    Lower at night, higher in the afternoon.
    """

    base_temperature = 22

    if 0 <= hour_of_day <= 5:
        base_temperature -= 3
    elif 6 <= hour_of_day <= 10:
        base_temperature += 1
    elif 11 <= hour_of_day <= 17:
        base_temperature += 6
    elif 18 <= hour_of_day <= 21:
        base_temperature += 3

    random_noise = random.uniform(-1.5, 1.5)

    return round(base_temperature + random_noise, 2)


# -----------------------------
# 3. Load curve simulation
# -----------------------------

def daily_load_curve(hour_of_day):
    """
    Base daily load curve for a commercial / institutional building.
    Return value is load factor.
    """

    if 0 <= hour_of_day <= 4:
        return 0.32          # deep night

    elif 5 <= hour_of_day <= 6:
        return 0.42          # early morning preparation

    elif 7 <= hour_of_day <= 8:
        return 0.58          # morning ramp-up

    elif 9 <= hour_of_day <= 11:
        return 0.72          # normal working hours

    elif 12 <= hour_of_day <= 14:
        return 0.82          # midday high load

    elif 15 <= hour_of_day <= 17:
        return 0.88          # afternoon peak

    elif 18 <= hour_of_day <= 20:
        return 0.68          # evening decline

    elif 21 <= hour_of_day <= 23:
        return 0.48          # late evening

    else:
        return 0.40

def apply_weekend_effect(load_factor, is_weekend):
    """
    Reduce building load during weekends.
    """

    if is_weekend:
        load_factor *= 0.80

    return load_factor


def apply_asset_behavior(load_factor, asset_type, temperature):
    """
    Adjust load factor according to asset type.

    Transformer:
        smoother and more stable

    Main Panel:
        follows building activity, slightly more variable

    HVAC Chiller:
        strongly affected by high temperature
    """

    if asset_type == "Transformer":
        load_factor += random.uniform(-0.03, 0.03)

    elif asset_type == "Main Panel":
        load_factor += random.uniform(-0.035, 0.045)

    elif asset_type == "HVAC Chiller":
        load_factor *= 0.75

        if temperature >= 26:
            load_factor += random.uniform(0.15, 0.25)
        else:
            load_factor += random.uniform(-0.04, 0.04)
    elif asset_type == "Lighting Panel":
        load_factor *= 0.65
        load_factor += random.uniform(-0.03, 0.03)

    elif asset_type == "HVAC Panel":
        load_factor *= 0.80
        if temperature >= 26:
            load_factor += random.uniform(0.12, 0.22)
        else:
            load_factor += random.uniform(-0.04, 0.04)

    elif asset_type == "EV Charger Panel":
        load_factor *= 0.72
        load_factor += random.uniform(-0.03, 0.18)

    return load_factor


def inject_peak_event(load_factor, asset_type, timestamp):
    """
    Add special high-load events.

    These events simulate realistic abnormal or peak operating conditions:
    - hot afternoon HVAC stress
    - main panel daytime peak
    - transformer building-wide peak
    - overnight unmanaged abnormal load
    - early morning equipment startup
    """

    hour = timestamp.hour
    day = timestamp.day
    event_date = timestamp.date()

    # 1. Hot afternoon HVAC stress event
    if asset_type == "HVAC Chiller" and day in [3, 4] and 14 <= hour <= 17:
        load_factor += random.uniform(0.25, 0.38)

    # 2. Main panel short daytime peak event
    if asset_type == "Main Panel" and event_date in [
        datetime(2026, 2, 12).date(),
        datetime(2026, 5, 8).date()
        ] and 10 <= hour <= 12:
        load_factor += random.uniform(0.18, 0.28)

    # 3. Transformer building-wide peak event
    if asset_type == "Transformer" and event_date in [
        datetime(2026, 2, 12).date(),
        datetime(2026, 5, 8).date()
        ] and 11 <= hour <= 13:
        load_factor += random.uniform(0.15, 0.25)

    # 4. Overnight abnormal load event
    # Example: equipment left running, unexpected overnight process, EV charging cluster, or cooling load anomaly
    if asset_type in ["Main Panel", "Transformer"] and day == 6 and 2 <= hour <= 4:
        load_factor += random.uniform(0.30, 0.45)

    # 5. Early morning startup event
    # Example: large motor / HVAC restart / building system startup
    if asset_type in ["Main Panel", "HVAC Chiller"] and day == 2 and 6 <= hour <= 7:
        load_factor += random.uniform(0.20, 0.32)

    # 6. Random rare spike
    # Low probability event that can happen at any time
    if random.random() < 0.002:
        load_factor += random.uniform(0.15, 0.25)

    return load_factor


def generate_load_factor(asset_type, hour_of_day, temperature, is_weekend, timestamp):
    """
    Generate final load factor using:

    base daily curve
    + weekend effect
    + asset-specific behavior
    + special peak events
    """

    load_factor = daily_load_curve(hour_of_day)

    load_factor = apply_weekend_effect(load_factor, is_weekend)

    load_factor = apply_asset_behavior(
        load_factor,
        asset_type,
        temperature
    )

    load_factor = inject_peak_event(
        load_factor,
        asset_type,
        timestamp
    )

    # Allow short-term overload simulation up to 115%
    load_factor = max(0.20, min(load_factor, 1.15))

    return load_factor


# -----------------------------
# 4. Voltage simulation
# -----------------------------

def generate_voltage(nominal_voltage, load_factor):
    """
    Simulate voltage behavior.

    Higher load causes slight voltage drop.
    """

    voltage_drop = 0

    if load_factor >= 0.80:
        voltage_drop += random.uniform(2, 6)

    if load_factor >= 0.95:
        voltage_drop += random.uniform(5, 10)

    random_noise = random.uniform(-1.2, 1.2)

    voltage = nominal_voltage - voltage_drop + random_noise

    return round(voltage, 2)


# -----------------------------
# 5. Record generation
# -----------------------------

def generate_one_record(asset, timestamp):
    """
    Generate one hourly measurement for one asset.
    """

    hour_of_day = timestamp.hour
    is_weekend = timestamp.weekday() >= 5

    temperature = generate_temperature(hour_of_day)

    load_factor = generate_load_factor(
        asset["asset_type"],
        hour_of_day,
        temperature,
        is_weekend,
        timestamp
    )

    voltage = generate_voltage(
        asset["nominal_voltage_V"],
        load_factor
    )

    target_power_kw = asset["capacity_kw"] * load_factor

    current_A = target_power_kw * 1000 / voltage

    record = {
        "timestamp": timestamp,
        "building_id": asset["building_id"],
        "asset_id": asset["asset_id"],
        "asset_type": asset["asset_type"],
        "nominal_voltage_V": asset["nominal_voltage_V"],
        "voltage_V": round(voltage, 2),
        "current_A": round(current_A, 2),
        "capacity_kw": asset["capacity_kw"],
        "ambient_temperature_C": temperature
    }

    return record


def generate_dataset():
    """
    Generate 1 building × 3 assets × 7 days hourly data.
    """

    records = []

    start_time = datetime(2026, 1, 1, 0, 0)
    total_hours = 181 * 24

    for hour_index in range(total_hours):
        timestamp = start_time + timedelta(hours=hour_index)

        for asset in ASSETS:
            record = generate_one_record(asset, timestamp)
            records.append(record)

    return records


# -----------------------------
# 6. Main program
# -----------------------------

def main():
    records = generate_dataset()

    df = pd.DataFrame(records)

    df = df.sort_values(["building_id", "asset_id", "timestamp"]).reset_index(drop=True)
    output_path = Path(__file__).parent.parent / "data" / "simulated_raw_load_data.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print(df.head())
    print()
    print(f"Generated rows: {len(df)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
