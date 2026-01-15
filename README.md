# Commercial_Property_Analytics_Suite
Automated Commercial Property Analytics Pipeline: Python ETL, SQL Modelling, and Power BI Dashboard


PROJECT BACKGROUND This project simulates a commercial scenario where data is fragmented into multiple files which themselves contain messy data in many different formats.

I wanted to build a system that could take a folder full of inconsistent Excel files, different layouts, different tenant names, and mixed units (sqm vs sqft) and automatically turn them into a clean, reliable dataset for analysis. The end goal was a Power BI dashboard that helps identify lease expiry risks and "wasted" rent, rather than just showing basic totals.

THE CHALLENGE (THE DATA) To test my code, I used a set of 100 "messy" files that simulate real-world errors, including:

Mixed Units: Some reports used Square Feet while others used Square Meters.

Inconsistent Naming: Tenants appeared as "Coles", "Coles Group", "Coles Ltd", etc.

Bad Formatting: Headers starting on different rows.

(You can see examples of these problem files in the raw_data_samples folder).

HOW IT WORKS

Python (The Cleaning Layer) I wrote file_cleaner.py to handle the heavy lifting. Instead of fixing files manually in Excel, this script:

Loops through the folder and identifies if a file is CSV or Excel.

Standardizes Units: It detects columns labeled "sqft" or "feet" and converts them to sqm so all areas are comparable.

Cleans Names: I used Regex to strip out suffixes like "Pty Ltd" or "Group" so I could group tenants accurately.

Consolidates: Merges everything into a single SQLite database (Property_Database.db).

SQL (The Logic Layer) Once the data was in SQLite, I used SQL to apply the business logic (Data_Transform.sql).

I created a central table called lease_facts.

Parent Grouping: I wrote a CASE WHEN statement to group individual brands into their parent companies (e.g., Wesfarmers Group, Woolworths Group).

WALE Calculation: Calculated the Weighted Average Lease Expiry (by income and area) to measure portfolio risk.

Power BI (The Dashboard) The final report connects to the database to visualize the strategy.

Expiry Profile: A bar chart showing exactly how much rent is expiring in each financial year.

Drill-down: The report allows filtering from the full Portfolio view down to State, Centre, and individual Tenant levels.

REPOSITORY CONTENTS

file_cleaner.py: The Python script that ingests and cleans the raw files.

Data_Transform.sql: The SQL queries used to build the final reporting table.

raw_data_samples/: A few example files showing the raw state of the data before processing.

TOOLS USED

Python: Pandas, SQLite3, Glob

SQL: SQLite

Visualization: Microsoft Power BI
