import pandas as pd
import numpy as np

# ============================================================================
# Customer Health Project: Health Score Engine
# ============================================================================
# Calculate comprehensive health scores for each customer based on usage,
# engagement, support, and commercial metrics

def calculate_usage_score(days_since_last_activity):
    """
    Calculate usage score based on recency of activity.
    
    Scoring:
    - 100: Activity within 7 days (very active)
    - 80:  Activity within 30 days (active)
    - 50:  Activity within 60 days (moderate)
    - 20:  Activity older than 60 days (inactive)
    """
    if pd.isna(days_since_last_activity):
        return 20  # No activity = lowest score
    
    days = int(days_since_last_activity)
    if days <= 7:
        return 100
    elif days <= 30:
        return 80
    elif days <= 60:
        return 50
    else:
        return 20


def calculate_engagement_score(unique_active_users, publish_events, export_events, integration_events):
    """
    Calculate engagement score based on user activity and feature adoption.
    
    Factors:
    - Number of unique active users
    - Usage of key features (publish, export, integration)
    - Capped at 100
    """
    # Base score from unique users (up to 50 points)
    user_score = min(unique_active_users * 5, 50)
    
    # Feature adoption score (up to 50 points)
    feature_score = min((publish_events + export_events + integration_events) / 10, 50)
    
    # Total engagement score (capped at 100)
    engagement = user_score + feature_score
    return min(engagement, 100)


def calculate_support_score(open_tickets, high_priority_tickets):
    """
    Calculate support score based on ticket health.
    
    Scoring:
    - Start at 100
    - Subtract 15 for each open ticket
    - Subtract 25 for each high priority ticket
    - Minimum 0
    """
    score = 100
    score -= open_tickets * 15
    score -= high_priority_tickets * 25
    return max(score, 0)


def calculate_commercial_score(payment_status, renewal_stage):
    """
    Calculate commercial score based on payment and renewal health.
    
    Scoring:
    - 100: paid + on track (ideal)
    - 70:  renewal_stage is unknown (uncertain)
    - 40:  overdue OR risk (warning)
    - 20:  overdue AND risk (critical)
    """
    is_paid = payment_status == "paid"
    is_overdue = payment_status == "overdue"
    is_on_track = renewal_stage == "on track"
    is_risk = renewal_stage == "risk"
    is_unknown = renewal_stage == "unknown"
    
    # Best case: paid and on track
    if is_paid and is_on_track:
        return 100
    
    # Unknown renewal stage
    if is_unknown:
        return 70
    
    # Worst case: both overdue and risk
    if is_overdue and is_risk:
        return 20
    
    # Warning case: either overdue OR risk
    if is_overdue or is_risk:
        return 40
    
    # Default
    return 50


def calculate_health_segment(health_score):
    """
    Classify customer into health segment based on score.
    
    Segments:
    - Healthy: score >= 75
    - Watchlist: score >= 50
    - At Risk: score < 50
    """
    if health_score >= 75:
        return "Healthy"
    elif health_score >= 50:
        return "Watchlist"
    else:
        return "At Risk"


def main():
    """Load metrics, calculate scores, and export results."""
    
    print("=" * 70)
    print("Customer Health Score Engine")
    print("=" * 70)
    
    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================
    print("\n[1/4] Loading customer metrics...")
    try:
        df = pd.read_csv("outputs/customer_metrics.csv")
        print(f"✅ Loaded {len(df)} customer records")
    except Exception as e:
        print(f"❌ Error loading metrics: {e}")
        return
    
    # ========================================================================
    # 2. CALCULATE COMPONENT SCORES
    # ========================================================================
    print("\n[2/4] Calculating component scores...")
    
    try:
        # Usage Score: based on activity recency
        df["usage_score"] = df["days_since_last_activity"].apply(calculate_usage_score)
        
        # Engagement Score: based on users and feature adoption
        df["engagement_score"] = df.apply(
            lambda row: calculate_engagement_score(
                row["unique_active_users"],
                row["publish_events"],
                row["export_events"],
                row["integration_events"]
            ),
            axis=1
        )
        
        # Support Score: based on ticket health
        df["support_score"] = df.apply(
            lambda row: calculate_support_score(
                row["open_tickets"],
                row["high_priority_tickets"]
            ),
            axis=1
        )
        
        # Commercial Score: based on payment and renewal status
        df["commercial_score"] = df.apply(
            lambda row: calculate_commercial_score(
                row["payment_status"],
                row["renewal_stage"]
            ),
            axis=1
        )
        
        print("✅ Component scores calculated")
        
    except Exception as e:
        print(f"❌ Error calculating component scores: {e}")
        return
    
    # ========================================================================
    # 3. CALCULATE FINAL HEALTH SCORE
    # ========================================================================
    print("\n[3/4] Calculating final health scores...")
    
    try:
        # Weighted composite score
        df["health_score"] = (
            df["usage_score"] * 0.40 +
            df["engagement_score"] * 0.25 +
            df["support_score"] * 0.20 +
            df["commercial_score"] * 0.15
        )
        
        # Round to 1 decimal place
        df["health_score"] = df["health_score"].round(1)
        
        # Health segment classification
        df["health_segment"] = df["health_score"].apply(calculate_health_segment)
        
        print("✅ Final health scores calculated")
        
    except Exception as e:
        print(f"❌ Error calculating final health score: {e}")
        return
    
    # ========================================================================
    # 4. EXPORT & SUMMARY
    # ========================================================================
    print("\n[4/4] Exporting results and generating summary...")
    
    try:
        # Select relevant columns for export
        export_cols = [
            "customer_id",
            "company_name",
            "contract_value",
            "usage_score",
            "engagement_score",
            "support_score",
            "commercial_score",
            "health_score",
            "health_segment"
        ]
        
        df_export = df[export_cols].copy()
        
        # Export to CSV
        output_path = "outputs/customer_health_scores.csv"
        df_export.to_csv(output_path, index=False)
        print(f"✅ Exported to {output_path}")
        
        # Generate summary statistics
        print("\n" + "=" * 70)
        print("PORTFOLIO HEALTH SUMMARY")
        print("=" * 70)
        
        segment_counts = df["health_segment"].value_counts()
        healthy = segment_counts.get("Healthy", 0)
        watchlist = segment_counts.get("Watchlist", 0)
        at_risk = segment_counts.get("At Risk", 0)
        
        print(f"\n📊 Health Segments:")
        print(f"   🟢 Healthy:   {healthy:3d} customers ({healthy/len(df)*100:5.1f}%)")
        print(f"   🟡 Watchlist: {watchlist:3d} customers ({watchlist/len(df)*100:5.1f}%)")
        print(f"   🔴 At Risk:   {at_risk:3d} customers ({at_risk/len(df)*100:5.1f}%)")
        
        avg_score = df["health_score"].mean()
        min_score = df["health_score"].min()
        max_score = df["health_score"].max()
        
        print(f"\n📈 Health Score Distribution:")
        print(f"   Average Score: {avg_score:6.1f} / 100")
        print(f"   Min Score:     {min_score:6.1f}")
        print(f"   Max Score:     {max_score:6.1f}")
        
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS! Health scores calculated for {len(df)} customers")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        return


if __name__ == "__main__":
    main()
