# PRD.md — TraceBack

## 1. Product Overview

**Product Name:** TraceBack — Network Incident Investigation Simulator

**Product Type:** Lightweight cybersecurity investigation web application

**Purpose:** TraceBack reconstructs a simulated network incident by correlating firewall, DNS, and login logs. It presents related events chronologically and generates an evidence summary to help users understand what happened and when.

**Target Users:** Students, cybersecurity beginners, and users learning basic network incident investigation.

**Project Duration:** 1 hour for the initial AI-assisted MVP.

## 2. Problem Statement

Network activity is recorded across different log sources, making it difficult for beginners to understand the sequence of events associated with a possible security incident.

TraceBack provides a simple interface to import or load sample network logs, correlate events using timestamps and IP addresses, visualize an investigation timeline, and generate a downloadable report.

## 3. Product Goals

- Import and display firewall, DNS, and login logs.
- Correlate potentially related events using simple, explainable rules.
- Reconstruct events in chronological order.
- Highlight suspicious activity for further investigation.
- Generate a summary of the observed evidence.
- Export investigation results for documentation.

### Out of Scope

- Real-time network monitoring.
- Live packet capture.
- Machine learning or AI-based attack detection.
- Automated incident response or blocking.
- Integration with enterprise SIEM platforms.
- Production-grade authentication or multi-user access.

## 4. Technology Stack

- **Language:** Python
- **Web interface:** Streamlit
- **Data processing:** Pandas
- **Visualization:** Plotly
- **Storage:** SQLite
- **Input format:** CSV
- **Report export:** CSV or TXT

The application should run locally without external APIs or paid services.

## 5. Functional Requirements

### FR-01: Dashboard

Display the following metrics:

- Total log events.
- Number of suspicious events.
- Number of unique IP addresses.
- Number of investigation groups or incidents identified by the implemented rules.

Include a short summary of the loaded dataset.

### FR-02: Log Import

Allow users to upload CSV log files or load bundled synthetic sample data.

Support three event categories:

1. **Firewall:** Timestamp, source IP, destination IP, action, and destination port.
2. **DNS:** Timestamp, source IP, queried domain, and resolved IP when available.
3. **Login:** Timestamp, source IP, username, and login status.

Normalize supported records into a common event structure containing:

- Timestamp
- Event type
- Source IP
- Destination IP, if applicable
- Description
- Source record identifier

Display imported records in a table.

### FR-03: Event Correlation

Implement simple rule-based correlation.

Rules:

- Identify repeated failed logins from the same source IP.
- Highlight a successful login following repeated failed attempts from the same IP within a configurable time window.
- Link DNS and firewall events when the available IP information and timestamps support a plausible relationship.
- Group potentially related events that share an IP address and occur within a configurable time window.

For every correlation, display a short explanation.

Do not treat a shared IP address or temporal proximity alone as proof of an attack. Label uncertain relationships as potential correlations.

### FR-04: Incident Timeline

Display events in chronological order using a Plotly timeline or equivalent chart.

The timeline must:

- Display event timestamps and event categories.
- Visually distinguish suspicious events.
- Allow users to inspect event details.
- Display related-event explanations where available.

A filterable event table may accompany the visualization.

### FR-05: Evidence Summary

Generate a summary for the selected investigation containing:

- Investigation identifier.
- Relevant time range.
- Involved IP addresses.
- Event counts by category.
- Chronological event sequence.
- Suspicious patterns identified by the implemented rules.
- Reasons for correlating events.
- Limitations and uncertainty.

The summary must be derived from the loaded dataset rather than hardcoded text.

### FR-06: Report Export

Allow users to download investigation results as CSV or TXT.

The exported report should include timestamps, event types, relevant IP addresses, event descriptions, correlation explanations, and the investigation summary.

### FR-07: Input Validation

Handle common input errors gracefully:

- Empty CSV files.
- Missing required columns.
- Invalid timestamps.
- Invalid IP addresses.
- Duplicate records.

Display informative warnings rather than crashing the application.

Invalid records should be flagged or excluded according to a documented validation policy.

## 6. User Interface

Use a clean, professional dark cybersecurity dashboard.

The interface should include four sections:

1. **Dashboard:** Summary metrics and incident overview.
2. **Log Viewer:** CSV upload, sample data loading, filters, and event table.
3. **Incident Timeline:** Chronological visualization and related events.
4. **Investigation Report:** Evidence summary and export controls.

Use clear labels, readable tables, consistent spacing, and restrained accent colors.

The design must prioritize usability over visual complexity.

## 7. Synthetic Dataset

Bundle sample CSV data that can be loaded without user uploads.

Include at least three scenarios:

### Scenario A: Normal Network Activity

- Ordinary DNS query.
- Successful or permitted outbound connection.
- Normal login event.

Expected result: Events appear chronologically without an unsupported incident alert.

### Scenario B: Suspicious Login Sequence

- Several failed login attempts from the same source IP.
- A successful login from that IP shortly afterward.

Expected result: The implemented rule highlights the sequence and explains why it requires investigation.

### Scenario C: Potentially Related Network Events

- DNS query from an internal host.
- Firewall connection involving the relevant destination.
- Login activity associated with the host within the configured time window.

Expected result: The timeline displays potentially related events and explains each relationship.

Use documentation-only or private IP ranges and reserved example domains for synthetic data. Do not use real credentials or actual sensitive logs.

## 8. Test Cases

| ID | Test | Expected Result |
|---|---|---|
| TC01 | Load bundled sample data | Events load and dashboard metrics update |
| TC02 | Load normal activity scenario | Events appear chronologically without an unjustified alert |
| TC03 | Load suspicious login scenario | Repeated failures followed by a success are highlighted |
| TC04 | Load potentially related network events | Supported event relationships and explanations appear |
| TC05 | Upload CSV with invalid timestamps | Invalid records are flagged or excluded with a warning |
| TC06 | Upload CSV with missing columns | Informative validation message appears |
| TC07 | Export an investigation report | File downloads with the selected investigation's evidence |
| TC08 | Change the event filter | Displayed records update to match the filter |

Record actual results and pass/fail status only after executing each test.

## 9. Non-Functional Requirements

- The application must run locally.
- The interface should be responsive enough for a standard desktop browser.
- Sample data should load quickly.
- Code should be modular and beginner-friendly.
- Errors should be handled without unnecessary application crashes.
- No external API keys or paid services should be required.
- Correlation rules should be understandable and reproducible.

## 10. Suggested Project Structure

```text
TraceBack/
├── app.py
├── engine.py
├── database.py
├── sample_data/
│   ├── firewall.csv
│   ├── dns.csv
│   └── login.csv
├── tests/
│   └── test_engine.py
├── requirements.txt
├── README.md
└── PRD.md
```

Keep the implementation compact. If separate modules make the initial build slower, combine related logic into fewer files while preserving readability.

## 11. Acceptance Criteria

The MVP is complete when:

- The application launches successfully.
- Bundled synthetic logs can be loaded.
- The dashboard displays metrics derived from the loaded data.
- Users can inspect and filter log records.
- The correlation engine identifies the documented example patterns.
- The timeline displays events chronologically.
- Related events include understandable explanations.
- A report can be downloaded.
- At least the core test cases have been executed and their results documented.

SQLite should be used for event persistence if feasible within the initial build. If storage is implemented, imported events must be retrievable from the database.

## 12. Deliverables

1. Working Streamlit application.
2. Synthetic sample datasets.
3. Source code and dependency file.
4. Test cases with recorded actual results.
5. Screenshots of the dashboard, imported logs, timeline, evidence summary, and report output.
6. README with setup and execution instructions.
7. This product requirements document.

## 13. Future Enhancements

Potential future improvements include:

- Importing logs from additional forensic tools.
- Host-centered event exploration.
- Evidence annotations and investigation notes.
- More advanced correlation rules.
- PDF report generation.
- Importing supported endpoint forensic timelines.

These enhancements are not required for the initial MVP.

## 14. Implementation Priority

**Priority 1:** Working application, synthetic data, log table, correlation rules, and timeline.

**Priority 2:** Evidence summary, report export, and basic validation.

**Priority 3:** Visual polish, SQLite persistence, and additional tests.

If time is limited, complete Priority 1 first and add the remaining features only after the core workflow works end to end.