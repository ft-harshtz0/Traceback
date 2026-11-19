# TraceBack — Network Incident Investigation Simulator

TraceBack reconstructs a simulated network incident by correlating firewall, DNS, and login logs. It presents related events chronologically and generates an evidence summary to help users understand what happened and when.

## 🚀 Key Features

- **Dashboard:** Real-time metrics for total events, suspicious events, unique IPs, and identified incident clusters.
- **Log Ingestion & Normalization:** Ingests Firewall, DNS, and Login logs from CSV or bundled scenarios with schema validation, invalid IP, and corrupt timestamp filtering.
- **Correlation Engine:**
  - Repeated failed logins (brute force detection).
  - Suspicious successful login following repeated failures.
  - Links DNS domain queries with subsequent firewall outbound connections.
  - Temporal and IP-based clustering into incident groups.
- **Incident Timeline:** Interactive chronological Plotly visualization with visual indicators for suspicious activity and correlation explanations.
- **Evidence Summary & Reporting:** In-depth evidence breakdowns, event sequencing, limitations disclosures, and one-click TXT/CSV downloads.
- **SQLite Persistence:** Retrievable database backend storing parsed and correlated telemetry.

---

## 🛠️ Setup & Execution

### 1. Requirements
Ensure Python 3.10+ is installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Launch the Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 3. Run Automated Tests
```bash
pytest tests/test_engine.py
```

---

## 📂 Project Structure

```text
Traceback/
├── app.py                  # Streamlit application UI
├── engine.py               # Ingestion, validation, and correlation engine
├── database.py             # SQLite persistence layer
├── sample_data/            # Synthetic sample datasets (Scenarios A, B, C)
│   ├── firewall.csv
│   ├── dns.csv
│   └── login.csv
├── tests/
│   └── test_engine.py      # Automated test suite (TC01-TC08)
├── requirements.txt        # Python package dependencies
├── PRD.md                  # Product Requirements Document
└── README.md               # User guide & documentation
```

