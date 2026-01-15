import pandas as pd
import sqlite3
import glob
import os

#New function to fix the column names
def fix_column_names(df):
    #create a dicitonary of possible key words in the columns
    schema_keywords = {
        'industry': ['industry', 'sector', 'group'],
        'tenant_name': ['tenant', 'lessee', 'occupant', 'entity'],
        'annual_rent': ['rent', 'passing', 'gross', 'annual', 'income'],
        'start_date': ['start', 'commence', 'commencement', 'effective'],
        'end_date': ['end', 'expiry', 'terminate', 'termination'],
        'area_sqft': ['foot', 'sqft', 'feet'],  
        'area_sqm': ['area', 'sqm', 'nla', 'gfa', 'square']  
    }
    new_names = {}
    #Create a loop that goes through each column in the dataframe
    for col in df.columns:
        col_clean = col.lower().strip()

        #go through our dictionary for keywords
        for standard_name, keywords in schema_keywords.items():
            for keyword in keywords:
                if keyword in col_clean:
                    new_names[col] = standard_name
                    break
            if col in new_names:  # Stop searching once we find a match
                break
    #rename the keywords if we found any matches
    if new_names:
        df = df.rename(columns=new_names)   
    return df

#-----------------------------------------
# READING THE DATA
#-----------------------------------------
all_data_frames = []
files = glob.glob("portfolio_data/*")

for file in files:
    filename = os.path.basename(file)
    df = None

    #We want to see what the file type is, if it is a CSV we assume it has no issues with formatting (eg header rows) and we can read it straight away, if it is an Excel file we need to first locate the header row and then read the data from there
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            #we check the first 10 rows to determine where the header row is by searching for tenant or lessee
            temp_df = pd.read_excel(file, nrows=10, header=None)
            header_row_index = None
            for i, row in temp_df.iterrows():
                row_lower = row.astype(str).str.lower()
                if row_lower.str.contains('tenant').any() or row_lower.str.contains('lessee').any():
                    header_row_index = i
                    break
            #now we read can add the data to our dataframe
            if header_row_index is not None:
                df = pd.read_excel(file, header=header_row_index)
            else:
                print(f"Header row not found in file: {filename}. Skipping this file.")
                continue
        #now we need to fix the column names
        if df is not None:
            df = fix_column_names(df)
            #We create a new column called Centre and set it to the first 8 characters of the filename
            df['Centre'] = filename[:8]
            all_data_frames.append(df)
        #if we do not find any columns we print a warning
        else:
            print(f"Could not read file: {filename}. Skipping this file.")
    #catch any errors and print them
    except Exception as e:
        print(f"Error reading file {filename}: {e}")

#Combine all dataframes into one
if all_data_frames:
    master_df = pd.concat(all_data_frames, ignore_index=True)
    print('Consolidation Complete')
    print(f"INITIAL ROW COUNT (before any cleaning): {len(master_df)}")
    print(master_df)
else:
    print("No data frames to consolidate.")


#-----------------------------------------
# CLEANING THE DATA
#-----------------------------------------

#Clean the annual rent column
def rentcleaner(master_df):
    # Remove any non-numeric characters and convert to float
    master_df['annual_rent'] = master_df['annual_rent'].astype(str).str.replace(r'[^0-9.-]', '', regex=True)
    master_df['annual_rent'] = pd.to_numeric(master_df['annual_rent'], errors='coerce')
    return master_df
master_df = rentcleaner(master_df)

#Clean the tenant names
# We need to catch the following issues:
# Spaces before or after the name
# capitalisation inconsistencies
# companies having pty ltd and other suffixes
def tenantcleaner(master_df):
    #we first strip spaces and standardise casing
    master_df['tenant_name'] = master_df['tenant_name'].astype(str).str.strip().str.title()
    #we catch suffixes
    #suffixes = ['Pty Ltd', 'Ltd', 'Group', 'Holdings']
    master_df['tenant_name'] = master_df['tenant_name'].str.replace(r'\s+Pty\s+Ltd\.?$', '', regex=True)
    #we need catch 'Coles Group' and convert to 'Coles'
    master_df['tenant_name'] = master_df['tenant_name'].str.replace(r'\s+Group$', '', regex=True)
    return master_df    
master_df = tenantcleaner(master_df)
#we will now print unique tenant names to identify variations and have them sorted for easier identification
print(sorted(master_df['tenant_name'].unique()))

#clean the dates making sure to assume we are not using USA date formats
def datecleaner(master_df):
    master_df['start_date'] = pd.to_datetime(master_df['start_date'], dayfirst=True, errors='coerce')
    master_df['end_date'] = pd.to_datetime(master_df['end_date'], dayfirst=True, errors='coerce')
    return master_df
master_df = datecleaner(master_df)

#We also want to add columns for year and month for both start and end dates
master_df['start_year'] = master_df['start_date'].dt.year
master_df['start_month'] = master_df['start_date'].dt.month
#convert month to worded month
master_df['start_month_name'] = master_df['start_month'].map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                                         7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

master_df['end_year'] = master_df['end_date'].dt.year
master_df['end_month'] = master_df['end_date'].dt.month
#convert month to worded month
master_df['end_month_name'] = master_df['end_month'].map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                                         7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

#clean the area_sqft column if it exists and convert to sqm BEFORE cleaning area_sqm
if 'area_sqft' in master_df.columns:
    def sqft_to_sqm(master_df):
        master_df['area_sqft'] = master_df['area_sqft'].astype(str).str.replace(r'[^0-9.-]', '', regex=True)
        master_df['area_sqft'] = pd.to_numeric(master_df['area_sqft'], errors='coerce')
        # Convert sqft to sqm (1 sqft = 0.092903 sqm)
        master_df['area_sqm_from_sqft'] = master_df['area_sqft'] * 0.092903
        return master_df
    master_df = sqft_to_sqm(master_df)
    
#Clean the area sqm column
def areacleaner(master_df):
    # Remove any non-numeric characters and convert to float
    if 'area_sqm' in master_df.columns:
        master_df['area_sqm'] = master_df['area_sqm'].astype(str).str.replace(r'[^0-9.-]', '', regex=True)
        master_df['area_sqm'] = pd.to_numeric(master_df['area_sqm'], errors='coerce')
    return master_df
master_df = areacleaner(master_df)

#If area_sqm_from_sqft exists, fill any NaN area_sqm values with it
if 'area_sqm_from_sqft' in master_df.columns:
    #If area_sqm is NaN, fill it with area_sqm_from_sqft
    master_df['area_sqm'] = master_df['area_sqm'].fillna(master_df['area_sqm_from_sqft'])
    #Drop the temporary area_sqm_from_sqft column as well as the original area_sqft column
    master_df = master_df.drop(columns=['area_sqm_from_sqft', 'area_sqft'])

print(f"Rows before dropping NaN: {len(master_df)}")
#drop any Nan dates that could not be converted
master_df = master_df.dropna(subset=['start_date', 'end_date'])
print(f"Rows after dropping bad dates: {len(master_df)}")
#Drop any rows with NaN in area_sqm
master_df = master_df.dropna(subset=['area_sqm'])
print(f"Rows after dropping bad areas: {len(master_df)}")

print("Data Cleaning Complete.")
print(master_df)


#-----------------------------------------
# SAVE THE CLEAN DATA TO SQLITE DATABASE
#-----------------------------------------
#Create new sqlite database
conn = sqlite3.connect('Property_Database.db')
#Save the cleaned dataframe to a new table
master_df.to_sql('portfolio_leases', conn, if_exists='replace', index=False)
print("Cleaned data saved to Property_Database.db in table portfolio_leases.")
#close the connection
conn.close()

#-----------------------------------------
# Create a excel file with the cleaned data
master_df.to_excel('Property_Database.xlsx', index=False)