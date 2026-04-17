import pandas as pd
import numpy as np

def load_and_process_data(csv_path="patients.csv"):
    df = pd.read_csv(csv_path)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['departure_date'] = pd.to_datetime(df['departure_date'])
    
    # Generate unique Date Dimension
    all_dates = pd.concat([df['arrival_date'], df['departure_date']]).unique()
    dim_date = pd.DataFrame({'date': all_dates})
    dim_date['date_id'] = dim_date['date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['day'] = dim_date['date'].dt.day
    dim_date['quarter'] = dim_date['date'].dt.quarter
    dim_date = dim_date.sort_values('date').reset_index(drop=True)
    
    # Generate Patient Dimension
    dim_patient = df[['patient_id', 'name', 'age']].drop_duplicates().copy()
    
    def calculate_age_group(age):
        if age < 18: return '<18'
        elif age < 35: return '18-34'
        elif age < 55: return '35-54'
        else: return '55+'
        
    dim_patient['age_group'] = dim_patient['age'].apply(calculate_age_group)
    
    # Snowflake Schema setup: Dim_Department (higher level) and Dim_Service (lower level)
    unique_services = df['service'].unique()
    dim_service = pd.DataFrame({'service_name': unique_services})
    dim_service['service_id'] = dim_service.index + 1
    
    def assign_department(service):
        if service in ['ICU', 'emergency']:
            return 'Critical Care'
        elif service in ['surgery']:
            return 'Surgical'
        else:
            return 'General Medicine'
            
    dim_service['department_name'] = dim_service['service_name'].apply(assign_department)
    
    # Dim_Department Dimension
    dim_department = dim_service[['department_name']].drop_duplicates().reset_index(drop=True)
    dim_department['department_id'] = dim_department.index + 1
    
    # Link Dim_Service to Dim_Department
    dim_service = dim_service.merge(dim_department, on='department_name', how='left')
    dim_service = dim_service[['service_id', 'service_name', 'department_id']]
    
    # Fact Table: Admissions
    fact_admissions = df.copy()
    fact_admissions['admission_id'] = fact_admissions.index + 1
    
    # Add foreign keys
    fact_admissions['arrival_date_id'] = fact_admissions['arrival_date'].dt.strftime('%Y%m%d').astype(int)
    fact_admissions['departure_date_id'] = fact_admissions['departure_date'].dt.strftime('%Y%m%d').astype(int)
    
    fact_admissions = fact_admissions.merge(dim_service, left_on='service', right_on='service_name', how='left')
    
    # Metrics
    fact_admissions['length_of_stay'] = (fact_admissions['departure_date'] - fact_admissions['arrival_date']).dt.days
    
    fact_admissions = fact_admissions[['admission_id', 'patient_id', 'service_id', 'arrival_date_id', 'departure_date_id', 'length_of_stay', 'satisfaction']]
    
    # Fact Constellation: Secondary Fact Table (Billing)
    # Synthesize billing data based on admissions and services
    np.random.seed(42)
    fact_billing = fact_admissions[['admission_id', 'patient_id', 'service_id', 'arrival_date_id']].copy()
    fact_billing.columns = ['billing_id', 'patient_id', 'service_id', 'date_id'] # Use arrival date as billing date for simplicity
    
    def calculate_cost(service_id):
        # 1-ICU/Emergency etc.. assume base costs
        base = np.random.randint(500, 2000)
        multiplier = {1: 3, 2: 2, 3: 1, 4: 5}.get(service_id, 1) # Arbitrary multipliers for different services
        return base * multiplier
        
    fact_billing['total_cost'] = fact_billing['service_id'].apply(calculate_cost)
    
    return {
        'Dim_Patient': dim_patient,
        'Dim_Date': dim_date,
        'Dim_Service': dim_service,
        'Dim_Department': dim_department,
        'Fact_Admissions': fact_admissions,
        'Fact_Billing': fact_billing
    }
