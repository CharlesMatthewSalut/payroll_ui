import streamlit as st
import pandas as pd
from datetime import datetime

def calculate_overtime(hours, rate):
    """Calculate overtime pay"""
    if pd.isna(hours) or hours == 0:
        return 0
    return float(hours) * float(rate)

def create_payroll_system():
    st.title("Payroll Management System")
    
    # Initialize session state for employee data if not exists
    if 'employees' not in st.session_state:
        st.session_state.employees = {
            'BERNARD': {'daily_rate': 400, 'weekly_rate': 2400},
            'ERIC': {'daily_rate': 700, 'weekly_rate': 4200},
            'HERACLEO MANATAD': {'daily_rate': 550, 'weekly_rate': 3300},
            'NENEO': {'daily_rate': 450, 'weekly_rate': 2700},
            'PEDRO': {'daily_rate': 800, 'weekly_rate': 4800},
            'RENIER DELANTAR': {'daily_rate': 500, 'weekly_rate': 3000},
            'ALCRIZ': {'daily_rate': 450, 'weekly_rate': 2700},
            'JEDDA MONTANEZ': {'daily_rate': 500, 'weekly_rate': 3000},
            'NICO MACARAYA': {'daily_rate': 650, 'weekly_rate': 3900},
            'ANGELO': {'daily_rate': 350, 'weekly_rate': 2100},
            'HANZ SALUT': {'daily_rate': 350, 'weekly_rate': 2100},
            'CHARLES SALUT': {'daily_rate': 350, 'weekly_rate': 2100}
        }

    # Date selection
    st.header("Pay Period")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")

    # Overtime rate
    overtime_rate = st.number_input("Overtime Rate per Hour (₱)", value=100)

    # Create tabs for different functions
    tab1, tab2 = st.tabs(["Employee Management", "Payroll Processing"])

    with tab1:
        st.subheader("Employee Information")
        
        # Add new employee
        st.write("Add New Employee")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Employee Name")
        with col2:
            new_daily = st.number_input("Daily Rate", min_value=0.0)
        with col3:
            new_weekly = st.number_input("Weekly Rate", min_value=0.0)
            
        if st.button("Add Employee"):
            if new_name and new_daily and new_weekly:
                st.session_state.employees[new_name] = {
                    'daily_rate': new_daily,
                    'weekly_rate': new_weekly
                }
                st.success(f"Added employee: {new_name}")

        # Display current employees
        st.write("Current Employees")
        employee_df = pd.DataFrame.from_dict(
            st.session_state.employees,
            orient='index',
            columns=['daily_rate', 'weekly_rate']
        )
        st.dataframe(employee_df)

    with tab2:
        st.subheader("Payroll Processing")
        
        # Employee selection
        selected_employee = st.selectbox(
            "Select Employee",
            options=list(st.session_state.employees.keys())
        )

        # Get employee rates
        employee_data = st.session_state.employees[selected_employee]
        
        # Overtime hours input
        st.write("Overtime Hours")
        col1, col2, col3 = st.columns(3)
        with col1:
            mon_ot = st.number_input("Monday OT", min_value=0.0)
            thu_ot = st.number_input("Thursday OT", min_value=0.0)
        with col2:
            tue_ot = st.number_input("Tuesday OT", min_value=0.0)
            fri_ot = st.number_input("Friday OT", min_value=0.0)
        with col3:
            wed_ot = st.number_input("Wednesday OT", min_value=0.0)
            sat_ot = st.number_input("Saturday OT", min_value=0.0)

        # Deductions
        st.write("Deductions")
        col1, col2, col3 = st.columns(3)
        with col1:
            cash_advance = st.number_input("Cash Advance", min_value=0.0)
        with col2:
            snacks = st.number_input("Snacks", min_value=0.0)
        with col3:
            sss = st.number_input("SSS Share", min_value=0.0)

        # Calculate totals
        if st.button("Calculate Pay"):
            # Calculate overtime
            total_ot_hours = mon_ot + tue_ot + wed_ot + thu_ot + fri_ot + sat_ot
            overtime_pay = total_ot_hours * overtime_rate
            
            # Calculate total deductions
            total_deductions = cash_advance + snacks + sss
            
            # Calculate final pay
            total_pay = employee_data['weekly_rate'] + overtime_pay - total_deductions
            
            # Display results
            st.write("---")
            st.subheader("Payroll Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Employee: {selected_employee}")
                st.write(f"Weekly Rate: ₱{employee_data['weekly_rate']:,.2f}")
                st.write(f"Overtime Hours: {total_ot_hours}")
                st.write(f"Overtime Pay: ₱{overtime_pay:,.2f}")
            with col2:
                st.write(f"Total Deductions: ₱{total_deductions:,.2f}")
                st.write(f"Final Pay: ₱{total_pay:,.2f}")

if __name__ == "__main__":
    create_payroll_system()