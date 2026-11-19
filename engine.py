"""
Engine module for TraceBack.
Handles parsing, validation, normalization, and correlation of network logs.
"""

import ipaddress
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

# Required columns per log type
SCHEMA_REQUIREMENTS = {
    "firewall": ["timestamp", "source_ip", "destination_ip", "action", "destination_port"],
    "dns": ["timestamp", "source_ip", "queried_domain", "resolved_ip"],
    "login": ["timestamp", "source_ip", "username", "login_status"]
}

def is_valid_ip(ip_str: Any) -> bool:
    """Validate IPv4 or IPv6 address string."""
    if not ip_str or not isinstance(ip_str, str):
        return False
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False

def parse_and_validate_csv(df: pd.DataFrame, log_type: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Validates CSV against schema, timestamps, and IP addresses.
    Returns (normalized_records, warnings).
    """
    warnings = []
    normalized_records = []
    
    if df.empty:
        warnings.append(f"{log_type.capitalize()} log is empty.")
        return normalized_records, warnings
        
    req_cols = SCHEMA_REQUIREMENTS.get(log_type, [])
    # Case-insensitive column matching
    col_map = {col.lower().strip(): col for col in df.columns}
    missing = [c for c in req_cols if c not in col_map]
    
    if missing:
        warnings.append(f"{log_type.capitalize()} log missing required columns: {', '.join(missing)}")
        return normalized_records, warnings
        
    # Standardize column names
    clean_df = df.rename(columns={col_map[c]: c for c in req_cols})
    
    # Check duplicate records
    dup_count = clean_df.duplicated().sum()
    if dup_count > 0:
        warnings.append(f"Ignored {dup_count} duplicate row(s) in {log_type} log.")
        clean_df = clean_df.drop_duplicates()
        
    for idx, row in clean_df.iterrows():
        # Timestamp validation
        raw_ts = str(row["timestamp"]).strip()
        try:
            ts = pd.to_datetime(raw_ts)
        except Exception:
            warnings.append(f"Row {idx+1} in {log_type}: Invalid timestamp '{raw_ts}'. Skipped.")
            continue
            
        # IP validation
        src_ip = str(row["source_ip"]).strip()
        if not is_valid_ip(src_ip):
            warnings.append(f"Row {idx+1} in {log_type}: Invalid source IP '{src_ip}'. Skipped.")
            continue
            
        record_id = f"{log_type}_{idx+1}_{int(ts.timestamp())}"
        rec = {
            "id": record_id,
            "timestamp": ts,
            "event_type": log_type,
            "source_ip": src_ip,
            "destination_ip": None,
            "description": "",
            "raw_details": {},
            "is_suspicious": False,
            "correlation_notes": [],
            "group_id": "GRP-DEFAULT"
        }
        
        if log_type == "firewall":
            dst_ip = str(row["destination_ip"]).strip()
            if not is_valid_ip(dst_ip):
                warnings.append(f"Row {idx+1} in firewall: Invalid destination IP '{dst_ip}'. Skipped.")
                continue
            action = str(row["action"]).upper().strip()
            port = str(row["destination_port"]).strip()
            rec["destination_ip"] = dst_ip
            rec["description"] = f"Firewall {action} traffic to {dst_ip}:{port}"
            rec["raw_details"] = {"action": action, "destination_port": port}
            
        elif log_type == "dns":
            domain = str(row["queried_domain"]).strip()
            res_ip = str(row["resolved_ip"]).strip() if pd.notna(row["resolved_ip"]) else None
            if res_ip and not is_valid_ip(res_ip):
                warnings.append(f"Row {idx+1} in dns: Invalid resolved IP '{res_ip}'. Ignored resolved IP.")
                res_ip = None
            rec["destination_ip"] = res_ip
            rec["description"] = f"DNS query for '{domain}' -> {res_ip if res_ip else 'NXDOMAIN/None'}"
            rec["raw_details"] = {"queried_domain": domain, "resolved_ip": res_ip}
            
        elif log_type == "login":
            user = str(row["username"]).strip()
            status = str(row["login_status"]).upper().strip()
            rec["description"] = f"Login {status} for user '{user}'"
            rec["raw_details"] = {"username": user, "login_status": status}
            
        normalized_records.append(rec)
        
    return normalized_records, warnings


def correlate_events(events: List[Dict[str, Any]], window_minutes: int = 15) -> List[Dict[str, Any]]:
    """
    Implements PRD FR-03 Correlation Rules:
    1. Repeated failed logins from same source IP.
    2. Successful login following repeated failed logins from same source IP.
    3. Link DNS and firewall events when destination IP and host match within time window.
    4. Group potentially related events sharing an IP address within the time window.
    """
    if not events:
        return []
        
    # Sort events chronologically
    sorted_events = sorted(events, key=lambda x: pd.to_datetime(x["timestamp"]))
    window = timedelta(minutes=window_minutes)
    
    # 1 & 2: Login correlation (Brute Force and Subsequent Success)
    login_events = [e for e in sorted_events if e["event_type"] == "login"]
    ip_failed_logins: Dict[str, List[Dict[str, Any]]] = {}
    
    for ev in login_events:
        ip = ev["source_ip"]
        status = ev["raw_details"].get("login_status")
        ts = pd.to_datetime(ev["timestamp"])
        
        if ip not in ip_failed_logins:
            ip_failed_logins[ip] = []
            
        # Clean up failures outside window
        ip_failed_logins[ip] = [f for f in ip_failed_logins[ip] if ts - pd.to_datetime(f["timestamp"]) <= window]
        
        if status == "FAILED":
            ip_failed_logins[ip].append(ev)
            if len(ip_failed_logins[ip]) >= 3:
                # Mark repeated failed logins as suspicious
                for f in ip_failed_logins[ip]:
                    f["is_suspicious"] = True
                    note = f"Multiple failed login attempts ({len(ip_failed_logins[ip])}+) from {ip} within {window_minutes}m."
                    if note not in f["correlation_notes"]:
                        f["correlation_notes"].append(note)
                        
        elif status == "SUCCESS":
            if len(ip_failed_logins[ip]) >= 3:
                # Highlight successful login following repeated failures
                ev["is_suspicious"] = True
                note = f"Successful login immediately following {len(ip_failed_logins[ip])} failed attempts from {ip}."
                if note not in ev["correlation_notes"]:
                    ev["correlation_notes"].append(note)
                # Clear counter after sequence
                ip_failed_logins[ip] = []
                
    # 3: Link DNS queries and Firewall connections
    dns_events = [e for e in sorted_events if e["event_type"] == "dns"]
    fw_events = [e for e in sorted_events if e["event_type"] == "firewall"]
    
    for dns in dns_events:
        resolved_ip = dns["raw_details"].get("resolved_ip")
        if not resolved_ip:
            continue
        dns_src = dns["source_ip"]
        dns_ts = pd.to_datetime(dns["timestamp"])
        domain = dns["raw_details"].get("queried_domain", "unknown")
        
        for fw in fw_events:
            fw_src = fw["source_ip"]
            fw_dst = fw.get("destination_ip")
            fw_ts = pd.to_datetime(fw["timestamp"])
            
            # Match source host and destination IP within window
            if dns_src == fw_src and resolved_ip == fw_dst:
                if timedelta(seconds=0) <= (fw_ts - dns_ts) <= window:
                    rel_note = f"Potential Correlation: Host {dns_src} queried domain '{domain}' resolving to {resolved_ip}, followed by outbound connection."
                    if rel_note not in dns["correlation_notes"]:
                        dns["correlation_notes"].append(rel_note)
                    if rel_note not in fw["correlation_notes"]:
                        fw["correlation_notes"].append(rel_note)
                        
    # 4: Group events by IP and temporal proximity
    group_counter = 1
    assigned = set()
    
    for i, e1 in enumerate(sorted_events):
        if e1["id"] in assigned:
            continue
            
        group_id = f"INC-{group_counter:03d}"
        e1["group_id"] = group_id
        assigned.add(e1["id"])
        
        e1_ips = {e1["source_ip"]}
        if e1.get("destination_ip"):
            e1_ips.add(e1["destination_ip"])
        t1 = pd.to_datetime(e1["timestamp"])
        
        for j in range(i + 1, len(sorted_events)):
            e2 = sorted_events[j]
            t2 = pd.to_datetime(e2["timestamp"])
            
            if t2 - t1 > window:
                break
                
            e2_ips = {e2["source_ip"]}
            if e2.get("destination_ip"):
                e2_ips.add(e2["destination_ip"])
                
            if e1_ips.intersection(e2_ips):
                e2["group_id"] = group_id
                assigned.add(e2["id"])
                
        group_counter += 1
        
    return sorted_events


def generate_evidence_summary(events: List[Dict[str, Any]], group_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates an evidence summary derived directly from the dataset (FR-05).
    """
    filtered = events
    if group_id and group_id != "All":
        filtered = [e for e in events if e.get("group_id") == group_id]
        
    if not filtered:
        return {
            "investigation_id": group_id or "N/A",
            "time_range": "No events found",
            "involved_ips": [],
            "event_counts": {},
            "event_sequence": [],
            "suspicious_patterns": [],
            "correlation_reasons": [],
            "limitations": "No data loaded to assess."
        }
        
    timestamps = [pd.to_datetime(e["timestamp"]) for e in filtered]
    earliest = min(timestamps).strftime("%Y-%m-%d %H:%M:%S")
    latest = max(timestamps).strftime("%Y-%m-%d %H:%M:%S")
    
    ips = set()
    counts = {"firewall": 0, "dns": 0, "login": 0}
    suspicious_patterns = []
    correlation_reasons = []
    
    for e in filtered:
        if e["source_ip"]:
            ips.add(e["source_ip"])
        if e.get("destination_ip"):
            ips.add(e["destination_ip"])
        etype = e.get("event_type")
        if etype in counts:
            counts[etype] += 1
        else:
            counts[etype] = 1
            
        if e.get("is_suspicious"):
            for note in e.get("correlation_notes", []):
                if note not in suspicious_patterns:
                    suspicious_patterns.append(note)
                    
        for note in e.get("correlation_notes", []):
            if note not in correlation_reasons:
                correlation_reasons.append(note)
                
    summary = {
        "investigation_id": group_id or "Aggregated-Investigation",
        "time_range": f"{earliest} to {latest}",
        "involved_ips": sorted(list(ips)),
        "event_counts": counts,
        "event_sequence": [
            f"[{e['timestamp']}] ({e['event_type'].upper()}) {e['source_ip']} -> {e.get('destination_ip') or 'N/A'}: {e['description']}"
            for e in filtered
        ],
        "suspicious_patterns": suspicious_patterns,
        "correlation_reasons": correlation_reasons,
        "limitations": (
            "Temporal proximity and shared IP addresses indicate potential correlation, "
            "not definitive proof of malicious activity or network intrusion. "
            "Network Address Translation (NAT) or multi-tenant proxies may associate unrelated hosts."
        )
    }
    return summary

