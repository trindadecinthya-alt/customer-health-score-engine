import sqlite3
import pandas as pd
import os

# ============================================================================
# Customer Health Project: Data Loading Script
# ============================================================================
# This script:
# 1. Creates SQLite database and tables
# 2. Loads CSV data into the database
# 3. Generates customer metrics
# 4. Exports results to CSV

def load_data():
    """Load data into SQLite database and generate customer metrics."""
    
    # Database connection
    db_path = "customer_health.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("Customer Health Project: Data Loading")
    print("=" * 70)
    
    # ========================================================================
    # 1. CREATE TABLES
    # ========================================================================
    print("\n[1/6] Creating tables from sql/create_tables.sql...")
    try:
        with open("sql/create_tables.sql", "r") as f:
            create_sql = f.read()
        cursor.executescript(create_sql)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.close()
        return
    
    # ========================================================================
    # 2. LOAD DATA: Customers
    # ========================================================================
    print("\n[2/6] Loading data/customers.csv...")
    try:
        customers_df = pd.read_csv("data/customers.csv")
        customers_df.to_sql("customers", conn, if_exists="append", index=False)
        print(f"✅ Loaded {len(customers_df)} customers")
    except Exception as e:
        print(f"❌ Error loading customers: {e}")
        conn.close()
        return
    
    # ========================================================================
    # 3. LOAD DATA: Usage Events
    # ========================================================================
    print("\n[3/6] Loading data/usage_events.csv...")
    try:
        usage_events_df = pd.read_csv("data/usage_events.csv")
        usage_events_df.to_sql("usage_events", conn, if_exists="append", index=False)
        print(f"✅ Loaded {len(usage_events_df)} usage events")
    except Exception as e:
        print(f"❌ Error loading usage events: {e}")
        conn.close()
        return
    
    # ========================================================================
    # 4. LOAD DATA: Support Tickets
    # ========================================================================
    print("\n[4/6] Loading data/support_tickets.csv...")
    try:
        support_tickets_df = pd.read_csv("data/support_tickets.csv")
        support_tickets_df.to_sql("support_tickets", conn, if_exists="append", index=False)
        print(f"✅ Loaded {len(support_tickets_df)} support tickets")
    except Exception as e:
        print(f"❌ Error loading support tickets: {e}")
        conn.close()
        return
    
    # ========================================================================
    # 5. LOAD DATA: Commercials
    # ========================================================================
    print("\n[5/6] Loading data/commercials.csv...")
    try:
        commercials_df = pd.read_csv("data/commercials.csv")
        commercials_df.to_sql("commercials", conn, if_exists="append", index=False)
        print(f"✅ Loaded {len(commercials_df)} commercial records")
    except Exception as e:
        print(f"❌ Error loading commercials: {e}")
        conn.close()
        return
    
    # ========================================================================
    # 6. GENERATE CUSTOMER METRICS & EXPORT
    # ========================================================================
    print("\n[6/6] Generating customer metrics...")
    try:
        # Read and execute the metrics query
        with open("sql/customer_metrics.sql", "r") as f:
            metrics_sql = f.read()
        
        metrics_df = pd.read_sql_query(metrics_sql, conn)
        
        # Create outputs folder if it doesn't exist
        os.makedirs("outputs", exist_ok=True)
        
        # Export to CSV
        output_path = "outputs/customer_metrics.csv"
        metrics_df.to_csv(output_path, index=False)
        
        print(f"✅ Generated customer metrics for {len(metrics_df)} customers")
        print(f"✅ Exported to {output_path}")
    except Exception as e:
        print(f"❌ Error generating metrics: {e}")
        conn.close()
        return
    
    # Close connection
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✅ SUCCESS! Data pipeline complete")
    print(f"   - Database: {db_path}")
    print(f"   - Metrics exported: outputs/customer_metrics.csv")
    print(f"   - Rows: {len(metrics_df)}")
    print("=" * 70)

if __name__ == "__main__":
    load_data()
