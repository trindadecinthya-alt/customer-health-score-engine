import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Customer Health Score Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .healthy { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); color: #333; }
        .watchlist { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #333; }
        .at-risk { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('outputs/customer_health_scores.csv')

df = load_data()

# Sidebar navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.radio(
    "Select View",
    ["📊 Dashboard", "🔍 Customer Search", "📈 Detailed Analysis", "💡 Recommendations"]
)

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
if page == "📊 Dashboard":
    st.title("📊 Customer Health Score Engine")
    st.markdown("Real-time SaaS customer health portfolio analysis and insights")
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Customers",
            len(df),
            delta="50 analyzed",
            delta_color="off"
        )
    
    with col2:
        avg_score = df['health_score'].mean()
        st.metric(
            "Average Health Score",
            f"{avg_score:.1f}/100",
            delta=f"Range: {df['health_score'].min():.1f} - {df['health_score'].max():.1f}",
            delta_color="off"
        )
    
    with col3:
        healthy_count = len(df[df['health_segment'] == 'Healthy'])
        pct = (healthy_count / len(df)) * 100
        st.metric(
            "🟢 Healthy",
            healthy_count,
            delta=f"{pct:.0f}%",
            delta_color="normal"
        )
    
    with col4:
        at_risk = len(df[df['health_segment'] == 'At Risk'])
        pct = (at_risk / len(df)) * 100
        st.metric(
            "🔴 At Risk",
            at_risk,
            delta=f"{pct:.0f}% - URGENT",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Health Segment Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Health Segment Distribution")
        segment_counts = df['health_segment'].value_counts()
        colors = {'Healthy': '#84fab0', 'Watchlist': '#fee140', 'At Risk': '#ff6b6b'}
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            segment_counts.values,
            labels=segment_counts.index,
            autopct='%1.1f%%',
            colors=[colors.get(x, '#ccc') for x in segment_counts.index],
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        st.pyplot(fig)
    
    with col2:
        st.subheader("📈 Health Score Distribution")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df['health_score'], bins=15, color='#667eea', edgecolor='black', alpha=0.7)
        ax.axvline(df['health_score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["health_score"].mean():.1f}')
        ax.set_xlabel('Health Score', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Customers', fontsize=12, weight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    
    st.markdown("---")
    
    # At-Risk & Top Performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Top At-Risk Customers")
        at_risk_df = df[df['health_segment'] == 'At Risk'].nlargest(5, 'health_score')[
            ['company_name', 'health_score', 'usage_score', 'engagement_score', 'support_score', 'commercial_score']
        ]
        if len(at_risk_df) > 0:
            st.dataframe(at_risk_df, use_container_width=True)
        else:
            st.info("✅ No at-risk customers identified")
    
    with col2:
        st.subheader("🟢 Top Healthy Customers")
        healthy_df = df[df['health_segment'] == 'Healthy'].nlargest(5, 'health_score')[
            ['company_name', 'health_score', 'usage_score', 'engagement_score', 'support_score', 'commercial_score']
        ]
        st.dataframe(healthy_df, use_container_width=True)

# ============================================================================
# PAGE 2: CUSTOMER SEARCH
# ============================================================================
elif page == "🔍 Customer Search":
    st.title("🔍 Customer Search & Details")
    st.markdown("Find and analyze individual customer health profiles")
    st.markdown("---")
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("Search by company name", placeholder="e.g., Company_1")
    
    with col2:
        segment_filter = st.multiselect(
            "Filter by health segment",
            options=['Healthy', 'Watchlist', 'At Risk'],
            default=['Healthy', 'Watchlist', 'At Risk']
        )
    
    with col3:
        score_range = st.slider(
            "Health score range",
            min_value=float(df['health_score'].min()),
            max_value=float(df['health_score'].max()),
            value=(float(df['health_score'].min()), float(df['health_score'].max()))
        )
    
    # Apply filters
    filtered_df = df[
        (df['company_name'].str.contains(search_term, case=False, na=False)) &
        (df['health_segment'].isin(segment_filter)) &
        (df['health_score'] >= score_range[0]) &
        (df['health_score'] <= score_range[1])
    ]
    
    st.markdown(f"**Found {len(filtered_df)} customer(s)**")
    st.markdown("---")
    
    if len(filtered_df) > 0:
        selected_customer = st.selectbox(
            "Select a customer to view details",
            filtered_df['company_name'].values
        )
        
        customer = df[df['company_name'] == selected_customer].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        segment_emoji = {
            'Healthy': '🟢',
            'Watchlist': '🟡',
            'At Risk': '🔴'
        }
        
        with col1:
            st.metric("Health Segment", f"{segment_emoji.get(customer['health_segment'])} {customer['health_segment']}")
        
        with col2:
            st.metric("Health Score", f"{customer['health_score']:.1f}/100")
        
        with col3:
            st.metric("Contract Value", f"${customer['contract_value']:,.0f}")
        
        with col4:
            st.metric("Customer ID", customer['customer_id'])
        
        st.markdown("---")
        
        # Component Scores
        st.subheader("📊 Component Scores")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Usage Score", f"{customer['usage_score']:.1f}", delta="Weight: 40%")
        
        with col2:
            st.metric("Engagement Score", f"{customer['engagement_score']:.1f}", delta="Weight: 25%")
        
        with col3:
            st.metric("Support Score", f"{customer['support_score']:.1f}", delta="Weight: 20%")
        
        with col4:
            st.metric("Commercial Score", f"{customer['commercial_score']:.1f}", delta="Weight: 15%")
        
        st.markdown("---")
        
        # Visualization
        st.subheader("📈 Score Breakdown")
        scores = {
            'Usage': customer['usage_score'],
            'Engagement': customer['engagement_score'],
            'Support': customer['support_score'],
            'Commercial': customer['commercial_score']
        }
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors_map = ['#84fab0', '#667eea', '#764ba2', '#f093fb']
        bars = ax.bar(scores.keys(), scores.values(), color=colors_map, edgecolor='black', linewidth=1.5)
        ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Perfect Score')
        ax.set_ylim(0, 110)
        ax.set_ylabel('Score', fontsize=12, weight='bold')
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        st.pyplot(fig)
    else:
        st.warning("No customers match your filters. Try adjusting your search.")

# ============================================================================
# PAGE 3: DETAILED ANALYSIS
# ============================================================================
elif page == "📈 Detailed Analysis":
    st.title("📈 Detailed Analysis")
    st.markdown("Deep dive into portfolio composition and trends")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 At-Risk Customers")
        top_at_risk = df.nlargest(10, 'health_score')[df['health_segment'] == 'At Risk'].copy()
        if len(top_at_risk) == 0:
            top_at_risk = df.nsmallest(10, 'health_score')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        top_at_risk_sorted = top_at_risk.sort_values('health_score')
        bars = ax.barh(top_at_risk_sorted['company_name'], top_at_risk_sorted['health_score'], color='#ff6b6b')
        ax.set_xlabel('Health Score', fontsize=11, weight='bold')
        ax.set_xlim(0, 100)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}', ha='left', va='center', fontsize=9)
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("📈 Average Score by Segment")
        segment_avg = df.groupby('health_segment')['health_score'].agg(['mean', 'count'])
        segment_avg = segment_avg.reindex(['Healthy', 'Watchlist', 'At Risk'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#84fab0', '#fee140', '#ff6b6b']
        bars = ax.bar(segment_avg.index, segment_avg['mean'], color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Average Health Score', fontsize=11, weight='bold')
        ax.set_ylim(0, 100)
        ax.axhline(y=df['health_score'].mean(), color='black', linestyle='--', linewidth=2, label='Portfolio Mean')
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
        
        # Add value and count labels
        for bar, (idx, row) in zip(bars, segment_avg.iterrows()):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.1f}\n(n={int(row["count"])})',
                   ha='center', va='bottom', fontsize=10, weight='bold')
        
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Full data table
    st.subheader("📋 Full Customer Database")
    
    display_df = df[['company_name', 'health_score', 'health_segment', 'usage_score', 
                      'engagement_score', 'support_score', 'commercial_score', 'contract_value']].copy()
    display_df = display_df.sort_values('health_score', ascending=False)
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="customer_health_scores.csv",
        mime="text/csv"
    )

# ============================================================================
# PAGE 4: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.title("💡 Recommended Actions")
    st.markdown("Strategic actions based on customer health signals")
    st.markdown("---")
    
    # Define recommendations based on segments
    recommendations = {
        "🔴 At Risk + Low Usage": {
            "color": "🔴",
            "count": len(df[(df['health_segment'] == 'At Risk') & (df['usage_score'] < 80)]),
            "action": "Trigger re-engagement campaigns (training, onboarding refresh)",
            "impact": "Could improve scores for at-risk customers"
        },
        "🔴 At Risk + High Support Load": {
            "color": "🔴",
            "count": len(df[(df['health_segment'] == 'At Risk') & (df['support_score'] < 50)]),
            "action": "Prioritize escalation and technical resolution",
            "impact": "Reduce support friction and improve satisfaction"
        },
        "🟡 Watchlist + Upcoming Renewal": {
            "color": "🟡",
            "count": len(df[(df['health_segment'] == 'Watchlist') & (df['commercial_score'] < 70)]),
            "action": "Schedule QBR and align on value realization",
            "impact": "Strengthen renewal confidence"
        },
        "🟢 Healthy + High Engagement": {
            "color": "🟢",
            "count": len(df[(df['health_segment'] == 'Healthy') & (df['engagement_score'] > 70)]),
            "action": "Identify expansion opportunities (upsell/cross-sell)",
            "impact": "Increase customer lifetime value"
        }
    }
    
    for rec_key, rec_data in recommendations.items():
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 3])
            
            with col1:
                st.metric("", rec_data['count'], delta="customers")
            
            with col2:
                st.subheader(rec_key)
            
            with col3:
                st.write(f"**Action:** {rec_data['action']}")
                st.write(f"**Impact:** {rec_data['impact']}")
            
            st.markdown("---")
    
    st.markdown("---")
    
    # Custom recommendation generator
    st.subheader("🎯 Generate Custom Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_segment = st.selectbox("Select segment", ['Healthy', 'Watchlist', 'At Risk'])
    
    with col2:
        custom_metric = st.selectbox("By metric", ['Usage Score', 'Engagement Score', 'Support Score', 'Commercial Score'])
    
    if st.button("Generate"):
        metric_map = {
            'Usage Score': 'usage_score',
            'Engagement Score': 'engagement_score',
            'Support Score': 'support_score',
            'Commercial Score': 'commercial_score'
        }
        
        metric_col = metric_map[custom_metric]
        segment_df = df[df['health_segment'] == custom_segment]
        low_performers = segment_df[segment_df[metric_col] < segment_df[metric_col].median()]
        
        st.success(f"**{len(low_performers)} customers in {custom_segment} segment with below-median {custom_metric}**")
        st.dataframe(low_performers[['company_name', 'health_score', metric_col]], use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>Customer Health Score Engine | Data-driven SaaS customer analytics</p>
    <p>© 2026 | Built with Python, Pandas, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
