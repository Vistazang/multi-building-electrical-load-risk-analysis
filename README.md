\# Multi-Building Electrical Load Risk Analysis and Mitigation Simulation



\## Project Overview



This project is a simulated electrical infrastructure analytics project for a multi-building facility / campus-style power system. It models 3 buildings and 8 monitored electrical assets, including transformers, main distribution panels, lighting, HVAC, and EV charging panels.



The project uses Python to generate simulated hourly electrical load data, analyze operating risk, simulate non-critical load reduction strategies, and create plots and summary outputs for Excel dashboard visualization.



This is an educational portfolio project. It is not a stamped engineering design, formal power flow study, SCADA system, or electrical code compliance tool.



\## System Scenario



The simulated system includes 3 buildings and 8 monitored assets:



\### Building A



\* Transformer\_A1

\* Main\_Panel\_A1

\* Lighting\_Panel\_A1



\### Building B



\* Transformer\_B1

\* Main\_Panel\_B1

\* HVAC\_Panel\_B1



\### Building C



\* Main\_Panel\_C1

\* EV\_Charger\_Panel\_C1



The equipment ratings were updated to align with a conceptual CAD Electrical single-line diagram. The Python model treats each monitored asset as an asset-level load monitoring point.



\## Tools Used



\* Python

\* pandas

\* matplotlib

\* NumPy

\* Excel

\* AutoCAD Electrical / CAD single-line diagram concept



\## Main Features



\* Generated a simulated 6-month hourly load dataset for 8 electrical assets across 3 buildings.

\* Modeled asset-specific load behavior, temperature effects, voltage, current, capacity, and peak events.

\* Calculated power demand, load percentage, capacity margin, load change rate, and sustained high-load conditions.

\* Implemented multi-factor risk scoring to classify operating conditions as Normal, Warning, or High Risk.

\* Simulated non-critical load reduction strategies for high-risk operating periods.

\* Generated daily peak load plots and hourly inspection plots using matplotlib.

\* Exported summary CSV files for Excel dashboard analysis.

\* Built an Excel dashboard with normalized equipment risk score, risk event charts, and red/yellow/green risk categories.

\* Created a conceptual CAD Electrical single-line diagram to connect monitored assets with electrical equipment hierarchy.



\## Risk Analysis Logic



The project evaluates operating risk using multiple indicators:



\* Load percentage

\* Capacity margin

\* Load change rate

\* Sustained high-load condition

\* Voltage behavior



Risk levels are assigned using a multi-factor risk score:



\* 0–1: Normal

\* 2–3: Warning

\* 4 or higher: High Risk



The 80% loading level is used as an engineering warning reference for monitoring purposes. It is not used as a formal electrical code compliance calculation.



\## Mitigation Simulation



The mitigation logic simulates operational load reduction actions, such as:



\* Non-critical lighting reduction

\* HVAC curtailment

\* EV charging demand response or delayed charging



The project compares original and mitigated load conditions to evaluate how simulated mitigation actions reduce equipment loading and risk levels.



\## Project Outputs



The project generates:



\* Simulated raw load data

\* Risk-analyzed data

\* Mitigated load data

\* Asset risk summary

\* Mitigation summary

\* Daily maximum load plots

\* Hourly inspection plots

\* Excel dashboard outputs



Example output folders:



```text

data/

outputs/plots/daily\_max/

outputs/plots/inspection\_hourly/

outputs/summary/

```



\## How to Run



Install required Python packages:



```bash

pip install -r requirements.txt

```



Run the full pipeline:



```bash

cd Code_base
python run_pipeline.py

```



The pipeline runs the data generation, risk analysis, mitigation analysis, plotting, and summary generation scripts.



\## Limitations



This project is a simulated portfolio project and does not include:



\* Formal power flow analysis

\* Short-circuit analysis

\* Protection coordination

\* Breaker sizing

\* Conductor sizing

\* CT/PT ratio selection

\* Relay settings

\* SCADA integration

\* Formal CEC compliance verification

\* Stamped engineering design



The CAD single-line diagram is conceptual and is used to visually align the simulated monitored assets with an electrical infrastructure layout.



\## Future Improvements



Potential future improvements include:



\* Add SQL database storage for simulated load data

\* Add Power BI or Streamlit dashboard

\* Improve upstream/downstream load dependency modeling

\* Add panel schedule mapping

\* Expand CAD metadata for equipment tags and drawing references

\* Add more detailed facility operation scenarios



