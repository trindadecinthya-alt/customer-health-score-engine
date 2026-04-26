import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# ============================================================================
# Customer Segmentation Strategy
# ============================================================================
# Create intentional risk patterns for realistic portfolio analysis
# - 15 Healthy customers
# - 20 Watchlist customers
# - 15 At Risk customers

today = datetime.today()

# ----------------------
# 1. Customers (with segmentation)
# ----------------------
n_healthy = 15
n_watchlist = 20
n_at_risk = 15
n_customers = n_healthy + n_watchlist + n_at_risk

customers_data = []

# ========================================================================
# HEALTHY SEGMENT (15 customers)
# ========================================================================
for i in range(1, n_healthy + 1):
    customers_data.append({
        "customer_id": f"C{str(i).zfill(3)}",
        "company_name": f"Company_{i}",
        "plan": np.random.choice(["Growth", "Enterprise"], p=[0.3, 0.7]),  # Higher-tier plans
        "industry": np.random.choice(["Tech", "Healthcare", "Finance", "Retail"]),
        "contract_value": np.random.randint(30000, 50000),  # Higher contract values
        "segment": "Healthy"
    })

# ========================================================================
# WATCHLIST SEGMENT (20 customers)
# ========================================================================
for i in range(n_healthy + 1, n_healthy + n_watchlist + 1):
    customers_data.append({
        "customer_id": f"C{str(i).zfill(3)}",
        "company_name": f"Company_{i}",
        "plan": np.random.choice(["Starter", "Growth", "Enterprise"], p=[0.4, 0.4, 0.2]),
        "industry": np.random.choice(["Tech", "Healthcare", "Finance", "Retail"]),
        "contract_value": np.random.randint(10000, 35000),  # Mid-range values
        "segment": "Watchlist"
    })

# ========================================================================
# AT RISK SEGMENT (15 customers)
# ========================================================================
for i in range(n_healthy + n_watchlist + 1, n_customers + 1):
    customers_data.append({
        "customer_id": f"C{str(i).zfill(3)}",
        "company_name": f"Company_{i}",
        "plan": np.random.choice(["Starter", "Growth"], p=[0.6, 0.4]),  # Lower-tier plans
        "industry": np.random.choice(["Tech", "Healthcare", "Finance", "Retail"]),
        "contract_value": np.random.randint(5000, 25000),  # Lower contract values
        "segment": "At Risk"
    })

customers = pd.DataFrame(customers_data)

# Renewal dates with segment-aware patterns
renewal_dates = []
for idx, row in customers.iterrows():
    if row["segment"] == "Healthy":
        # Healthy: renewal dates spread over next 12 months
        days_to_renewal = random.randint(30, 365)
    elif row["segment"] == "Watchlist":
        # Watchlist: more urgent renewals (30-90 days)
        days_to_renewal = random.randint(30, 90) if random.random() > 0.5 else random.randint(90, 180)
    else:  # At Risk
        # At Risk: some overdue, some coming very soon
        if random.random() > 0.6:
            days_to_renewal = random.randint(-90, 0)  # Already overdue
        else:
            days_to_renewal = random.randint(1, 30)  # Very soon
    
    renewal_dates.append(today + timedelta(days=days_to_renewal))

customers["renewal_date"] = renewal_dates

# ----------------------
# 2. Usage Events (6 months)
# ----------------------
events = []
event_types = ["login", "publish", "export", "integration"]

for idx, cust in enumerate(customers.itertuples()):
    customer_id = cust.customer_id
    segment = cust.segment
    
    # Segment-aware event generation
    if segment == "Healthy":
        # Healthy: 150-250 events, recent activity
        n_events = random.randint(150, 250)
        days_range = 30  # Recent activity (last 30 days)
    elif segment == "Watchlist":
        # Watchlist: 50-150 events, moderate recency
        n_events = random.randint(50, 150)
        days_range = 90  # Last 90 days
    else:  # At Risk
        # At Risk: 5-50 events, stale activity
        n_events = random.randint(5, 50)
        days_range = 180  # Last 180 days (older activity)
    
    for _ in range(n_events):
        event_date = today - timedelta(days=random.randint(0, days_range))
        events.append([
            customer_id,
            event_date,
            random.choice(event_types),
            f"U{random.randint(1,10)}"
        ])

usage_events = pd.DataFrame(events, columns=[
    "customer_id", "event_date", "event_type", "user_id"
])

# ----------------------
# 3. Support Tickets (~150)
# ----------------------
tickets = []
ticket_count = 0

for idx, cust in enumerate(customers.itertuples()):
    customer_id = cust.customer_id
    segment = cust.segment
    
    # Segment-aware ticket generation
    if segment == "Healthy":
        # Healthy: 0-2 tickets, mostly closed, low priority
        n_tickets = random.randint(0, 2)
        priority_weights = {"low": 0.7, "medium": 0.25, "high": 0.05}
        status_weights = {"open": 0.2, "closed": 0.8}
    elif segment == "Watchlist":
        # Watchlist: 2-5 tickets, mixed status/priority
        n_tickets = random.randint(2, 5)
        priority_weights = {"low": 0.4, "medium": 0.4, "high": 0.2}
        status_weights = {"open": 0.5, "closed": 0.5}
    else:  # At Risk
        # At Risk: 4-10 tickets, mostly open, higher priority
        n_tickets = random.randint(4, 10)
        priority_weights = {"low": 0.2, "medium": 0.3, "high": 0.5}
        status_weights = {"open": 0.7, "closed": 0.3}
    
    for _ in range(n_tickets):
        ticket_count += 1
        created_date = today - timedelta(days=random.randint(0, 180))
        tickets.append([
            f"T{ticket_count}",
            customer_id,
            created_date,
            np.random.choice(
                list(priority_weights.keys()),
                p=list(priority_weights.values())
            ),
            np.random.choice(
                list(status_weights.keys()),
                p=list(status_weights.values())
            )
        ])

support_tickets = pd.DataFrame(tickets, columns=[
    "ticket_id", "customer_id", "created_date", "priority", "status"
])

# ----------------------
# 4. Commercials
# ----------------------
commercials = customers[["customer_id"]].copy()

# Payment status and renewal stage based on segment
payment_statuses = []
renewal_stages = []
for idx, row in customers.iterrows():
    segment = row["segment"]
    
    if segment == "Healthy":
        # Healthy: always paid, always on track
        payment_statuses.append("paid")
        renewal_stages.append("on track")
    elif segment == "Watchlist":
        # Watchlist: mostly paid, mixed renewal status
        payment_statuses.append(np.random.choice(["paid", "overdue"], p=[0.9, 0.1]))
        renewal_stages.append(np.random.choice(["on track", "unknown", "risk"], p=[0.6, 0.3, 0.1]))
    else:  # At Risk
        # At Risk: higher chance of overdue, risk or unknown renewal
        payment_statuses.append(np.random.choice(["paid", "overdue"], p=[0.4, 0.6]))
        renewal_stages.append(np.random.choice(["on track", "unknown", "risk"], p=[0.1, 0.3, 0.6]))

commercials["payment_status"] = payment_statuses
commercials["renewal_stage"] = renewal_stages

commercials["last_qbr_date"] = [
    today - timedelta(days=random.randint(30, 180))
    for _ in range(len(customers))
]

# ----------------------
# Save files
# ----------------------
# Remove segment column (was only for generation logic)
customers_export = customers.drop("segment", axis=1)

customers_export.to_csv("data/customers.csv", index=False)
usage_events.to_csv("data/usage_events.csv", index=False)
support_tickets.to_csv("data/support_tickets.csv", index=False)
commercials.to_csv("data/commercials.csv", index=False)

print("✅ Dataset created!")