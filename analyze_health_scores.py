import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ============================================================================
# Customer Health Project: Analysis & Insights
# ============================================================================
# Generate visualizations and business insights from health scores

def main():
    """Load health scores and generate analysis artifacts."""
    
    print("=" * 70)
    print("Customer Health Project: Analysis & Insights Engine")
    print("=" * 70)
    
    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================
    print("\n[1/5] Loading health scores...")
    try:
        df = pd.read_csv("outputs/customer_health_scores.csv")
        print(f"✅ Loaded {len(df)} customer records")
    except Exception as e:
        print(f"❌ Error loading health scores: {e}")
        return
    
    # ========================================================================
    # 2. CREATE CHARTS FOLDER
    # ========================================================================
    print("\n[2/5] Creating charts folder...")
    try:
        os.makedirs("outputs/charts", exist_ok=True)
        print("✅ Charts folder ready")
    except Exception as e:
        print(f"❌ Error creating charts folder: {e}")
        return
    
    # ========================================================================
    # 3. GENERATE VISUALIZATIONS
    # ========================================================================
    print("\n[3/5] Generating visualizations...")
    
    try:
        # ====================================================================
        # Chart 1: Health Segment Distribution (Pie Chart)
        # ====================================================================
        plt.figure(figsize=(10, 6))
        segment_counts = df["health_segment"].value_counts()
        colors = {"Healthy": "#2ecc71", "Watchlist": "#f39c12", "At Risk": "#e74c3c"}
        color_list = [colors.get(seg, "#95a5a6") for seg in segment_counts.index]
        
        wedges, texts, autotexts = plt.pie(
            segment_counts.values,
            labels=segment_counts.index,
            autopct="%1.1f%%",
            colors=color_list,
            startangle=90,
            textprops={"fontsize": 12, "weight": "bold"}
        )
        
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(11)
        
        plt.title("Customer Health Segment Distribution", fontsize=14, weight="bold", pad=20)
        plt.tight_layout()
        plt.savefig("outputs/charts/health_segment_distribution.png", dpi=300, bbox_inches="tight")
        plt.close()
        print("   ✅ health_segment_distribution.png")
        
        # ====================================================================
        # Chart 2: Health Score Distribution (Histogram)
        # ====================================================================
        plt.figure(figsize=(12, 6))
        plt.hist(df["health_score"], bins=15, color="#3498db", edgecolor="black", alpha=0.7)
        plt.axvline(df["health_score"].mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {df['health_score'].mean():.1f}")
        plt.axvline(75, color="green", linestyle="--", linewidth=2, label="Healthy Threshold (75)")
        plt.axvline(50, color="orange", linestyle="--", linewidth=2, label="Watchlist Threshold (50)")
        
        plt.xlabel("Health Score", fontsize=11, weight="bold")
        plt.ylabel("Number of Customers", fontsize=11, weight="bold")
        plt.title("Customer Health Score Distribution", fontsize=14, weight="bold", pad=20)
        plt.legend(loc="upper right", fontsize=10)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("outputs/charts/health_score_distribution.png", dpi=300, bbox_inches="tight")
        plt.close()
        print("   ✅ health_score_distribution.png")
        
        # ====================================================================
        # Chart 3: Top 10 At-Risk Customers (Bar Chart)
        # ====================================================================
        at_risk = df[df["health_segment"] == "At Risk"].sort_values("health_score").head(10)
        
        if len(at_risk) > 0:
            plt.figure(figsize=(12, 6))
            bars = plt.barh(at_risk["company_name"], at_risk["health_score"], color="#e74c3c", edgecolor="black")
            
            # Color gradient for bars
            for i, (bar, score) in enumerate(zip(bars, at_risk["health_score"])):
                if score < 30:
                    bar.set_color("#c0392b")  # Dark red
                elif score < 50:
                    bar.set_color("#e74c3c")  # Red
                else:
                    bar.set_color("#e67e22")  # Orange-red
            
            plt.xlabel("Health Score", fontsize=11, weight="bold")
            plt.title("Top 10 At-Risk Customers", fontsize=14, weight="bold", pad=20)
            plt.xlim(0, 100)
            
            # Add score labels on bars
            for i, (bar, score) in enumerate(zip(bars, at_risk["health_score"])):
                plt.text(score + 1, bar.get_y() + bar.get_height()/2, f"{score:.1f}", 
                        va="center", fontsize=9, weight="bold")
            
            plt.grid(axis="x", alpha=0.3)
            plt.tight_layout()
            plt.savefig("outputs/charts/top_10_at_risk_customers.png", dpi=300, bbox_inches="tight")
            plt.close()
            print("   ✅ top_10_at_risk_customers.png")
        else:
            print("   ⚠️  No at-risk customers to display")
        
        # ====================================================================
        # Chart 4: Average Score by Plan (Bar Chart)
        # ====================================================================
        # Merge plan data from original metrics
        metrics_df = pd.read_csv("outputs/customer_metrics.csv")
        df_with_plan = df.merge(metrics_df[["customer_id", "plan"]], on="customer_id", how="left")
        
        plan_scores = df_with_plan.groupby("plan")["health_score"].agg(["mean", "count"]).round(1)
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(plan_scores.index, plan_scores["mean"], color=["#3498db", "#2ecc71", "#9b59b6"], 
                       edgecolor="black", alpha=0.7)
        
        # Add value labels on bars
        for bar, (plan, row) in zip(bars, plan_scores.iterrows()):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{row['mean']:.1f}\n(n={int(row['count'])})",
                    ha="center", va="bottom", fontsize=10, weight="bold")
        
        plt.ylabel("Average Health Score", fontsize=11, weight="bold")
        plt.xlabel("Plan Type", fontsize=11, weight="bold")
        plt.title("Average Health Score by Plan", fontsize=14, weight="bold", pad=20)
        plt.ylim(0, 100)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig("outputs/charts/average_score_by_plan.png", dpi=300, bbox_inches="tight")
        plt.close()
        print("   ✅ average_score_by_plan.png")
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        return
    
    # ========================================================================
    # 4. GENERATE INSIGHTS SUMMARY
    # ========================================================================
    print("\n[4/5] Generating insights summary...")
    
    try:
        # Calculate key metrics
        total_customers = len(df)
        avg_score = df["health_score"].mean()
        
        # Segment stats
        segment_stats = df["health_segment"].value_counts()
        healthy_count = segment_stats.get("Healthy", 0)
        watchlist_count = segment_stats.get("Watchlist", 0)
        at_risk_count = segment_stats.get("At Risk", 0)
        
        # Top 5 at-risk customers with full details
        top_5_at_risk = df[df["health_segment"] == "At Risk"].nsmallest(5, "health_score")
        
        # Merge with detailed metrics
        detailed_metrics = pd.read_csv("outputs/customer_metrics.csv")
        top_5_detailed = top_5_at_risk.merge(detailed_metrics[["customer_id", "days_since_last_activity", "open_tickets", "high_priority_tickets", "payment_status", "renewal_stage", "contract_value"]], on="customer_id", how="left")
        
        # Generate summary text
        summary_lines = []
        summary_lines.append("=" * 70)
        summary_lines.append("CUSTOMER HEALTH ANALYSIS SUMMARY")
        summary_lines.append("=" * 70)
        summary_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        summary_lines.append("\n" + "=" * 70)
        summary_lines.append("PORTFOLIO OVERVIEW")
        summary_lines.append("=" * 70)
        
        summary_lines.append(f"\nTotal Customers:           {total_customers}")
        summary_lines.append(f"Average Health Score:      {avg_score:.1f} / 100")
        
        summary_lines.append("\n" + "-" * 70)
        summary_lines.append("HEALTH SEGMENT BREAKDOWN")
        summary_lines.append("-" * 70)
        
        summary_lines.append(f"\n🟢 Healthy:    {healthy_count:3d} customers ({healthy_count/total_customers*100:5.1f}%)")
        summary_lines.append(f"   • No current concerns")
        summary_lines.append(f"   • Strong engagement and payment standing")
        
        summary_lines.append(f"\n🟡 Watchlist:  {watchlist_count:3d} customers ({watchlist_count/total_customers*100:5.1f}%)")
        summary_lines.append(f"   • Requires monitoring")
        summary_lines.append(f"   • Mixed indicators across dimensions")
        
        summary_lines.append(f"\n🔴 At Risk:    {at_risk_count:3d} customers ({at_risk_count/total_customers*100:5.1f}%)")
        summary_lines.append(f"   • Immediate action recommended")
        summary_lines.append(f"   • Critical issues in usage, support, or commercial")
        
        summary_lines.append("\n" + "=" * 70)
        summary_lines.append("TOP 5 AT-RISK CUSTOMERS (Priority List)")
        summary_lines.append("=" * 70)
        
        for idx, (cid, row) in enumerate(top_5_detailed.iterrows(), 1):
            summary_lines.append(f"\n{idx}. {row['company_name']} ({row['customer_id']})")
            summary_lines.append(f"   Health Score:              {row['health_score']:.1f} / 100")
            days_activity = row.get('days_since_last_activity', 'N/A')
            summary_lines.append(f"   Days Since Last Activity:  {int(days_activity) if pd.notna(days_activity) else 'N/A'}")
            summary_lines.append(f"   Open Tickets:              {int(row['open_tickets'])}")
            summary_lines.append(f"   High-Priority Tickets:     {int(row['high_priority_tickets'])}")
            payment_status = row.get('payment_status_y', row.get('payment_status', 'N/A'))
            renewal_stage = row.get('renewal_stage_y', row.get('renewal_stage', 'N/A'))
            summary_lines.append(f"   Payment Status:            {payment_status}")
            summary_lines.append(f"   Renewal Stage:             {renewal_stage}")
            contract = row.get('contract_value_y', row.get('contract_value', 0))
            summary_lines.append(f"   Contract Value:            ${int(contract):,}")
        
        summary_lines.append("\n" + "=" * 70)
        summary_lines.append("RECOMMENDED CUSTOMER SUCCESS ACTIONS")
        summary_lines.append("=" * 70)
        
        summary_lines.append("\n1. ENGAGEMENT RECOVERY (At-Risk Segment)")
        summary_lines.append("   └─ Action: Immediate outreach to customers with >60 days inactivity")
        summary_lines.append("   └─ Focus: Understand barriers to adoption")
        summary_lines.append("   └─ Goal: Schedule onboarding review or executive QBR")
        summary_lines.append(f"   └─ Impact: Could improve scores for {at_risk_count} at-risk customers")
        
        summary_lines.append("\n2. SUPPORT TICKET RESOLUTION (Watchlist & At-Risk)")
        # Merge health scores with metrics to get ticket counts
        df_merged = df.merge(detailed_metrics[["customer_id", "total_tickets", "high_priority_tickets", "payment_status", "renewal_stage"]], on="customer_id", how="left")
        watchlist_and_risk = df_merged[df_merged["health_segment"].isin(["Watchlist", "At Risk"])]
        watchlist_with_tickets = watchlist_and_risk["total_tickets"].sum()
        high_priority_total = watchlist_and_risk["high_priority_tickets"].sum()
        summary_lines.append(f"   └─ Action: Triage and resolve {high_priority_total:.0f} high-priority tickets")
        summary_lines.append(f"   └─ Focus: Clear backlog of {watchlist_with_tickets:.0f} total open issues")
        summary_lines.append("   └─ Goal: Reduce escalation risk")
        summary_lines.append(f"   └─ Impact: Could lift {watchlist_count + at_risk_count} customers to Healthy")
        
        summary_lines.append("\n3. PAYMENT & RENEWAL RISK MITIGATION (Commercial Focus)")
        overdue_customers = df_merged[df_merged["payment_status"] == "overdue"].shape[0]
        at_risk_renewal = df_merged[df_merged["renewal_stage"] == "risk"].shape[0]
        summary_lines.append(f"   └─ Action: Contact {overdue_customers} customers with overdue payments")
        summary_lines.append(f"   └─ Focus: Renewal conversations with {at_risk_renewal} at-risk customers")
        summary_lines.append("   └─ Goal: Secure commitments and normalize payment")
        summary_lines.append(f"   └─ Impact: Prevent churn and revenue leakage")
        
        summary_lines.append("\n" + "=" * 70)
        summary_lines.append("END OF REPORT")
        summary_lines.append("=" * 70)
        
        # Write summary file
        summary_text = "\n".join(summary_lines)
        with open("outputs/health_insights_summary.txt", "w") as f:
            f.write(summary_text)
        
        print("✅ health_insights_summary.txt")
        
    except Exception as e:
        print(f"❌ Error generating insights summary: {e}")
        return
    
    # ========================================================================
    # 5. FINAL SUMMARY
    # ========================================================================
    print("\n[5/5] Analysis complete")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nGenerated artifacts:")
    print(f"  📊 outputs/charts/")
    print(f"     ├── health_segment_distribution.png")
    print(f"     ├── health_score_distribution.png")
    print(f"     ├── top_10_at_risk_customers.png")
    print(f"     └── average_score_by_plan.png")
    print(f"\n  📋 outputs/health_insights_summary.txt")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
