import streamlit as st
import pandas as pd
from decimal import Decimal
from datetime import datetime
import json

class PayrollSystem:
    def __init__(self):
        self.load_data()
        self.overtime_rate = Decimal('100')
    
    def load_data(self):
        if 'employees' not in st.session_state:
            st.session_state.employees = {}
            # Load initial data
            initial_data = [
                (1, "BERNARD", 400, 2400),
                (2, "ERIC", 700, 4200),
                (3, "HERACLEO MANATAD", 550, 3300),
                (4, "NENEO", 450, 2700),
                (5, "PEDRO", 800, 4800),
                (6, "RENIER DELANTAR", 500, 3000),
                (7, "ALCRIZ", 450, 2700),
                (8, "JEDDA MONTANEZ", 500, 3000),
                (9, "NICO MACARAYA", 650, 3900),
                (10, "ANGELO", 350, 2100),
                (11, "HANZ SALUT", 350, 2100),
                (12, "CHARLES SALUT", 350, 2100)
            ]
            for emp_id, name, daily_rate, weekly_rate in initial_data:
                self.add_employee(emp_id, name, daily_rate, weekly_rate)
    
    def add_employee(self, id, name, daily_rate, weekly_rate):
        st.session_state.employees[id] = {
            'name': name,
            'daily_rate': Decimal(str(daily_rate)),
            'weekly_rate': Decimal(str(weekly_rate)),
            'overtime_hours': Decimal('0'),
            'deductions': {
                'cash_advance': Decimal('0'),
                'snacks': Decimal('0'),
                'sss_share': Decimal('0')
            }
        }
    
    def update_employee(self, id, name, daily_rate, weekly_rate):
        if id in st.session_state.employees:
            emp = st.session_state.employees[id]
            emp['name'] = name
            emp['daily_rate'] = Decimal(str(daily_rate))
            emp['weekly_rate'] = Decimal(str(weekly_rate))
    
    def delete_employee(self, id):
        if id in st.session_state.employees:
            del st.session_state.employees[id]
    
    def get_employee_data(self):
        data = []
        for id, emp in st.session_state.employees.items():
            data.append({
                'ID': id,
                'Name': emp['name'],
                'Daily Rate': float(emp['daily_rate']),
                'Weekly Rate': float(emp['weekly_rate']),
                'Overtime Hours': float(emp['overtime_hours']),
                'Cash Advance': float(emp['deductions']['cash_advance']),
                'Snacks': float(emp['deductions']['snacks']),
                'SSS Share': float(emp['deductions']['sss_share'])
            })
        return pd.DataFrame(data)

def main():
    st.title('Payroll Management System')
    
    payroll = PayrollSystem()
    
    # Sidebar for adding new employees
    with st.sidebar:
        st.header('Add New Employee')
        new_id = st.number_input('Employee ID', min_value=1, step=1)
        new_name = st.text_input('Name')
        new_daily_rate = st.number_input('Daily Rate', min_value=0.0)
        new_weekly_rate = st.number_input('Weekly Rate', min_value=0.0)
        
        if st.button('Add Employee'):
            payroll.add_employee(new_id, new_name, new_daily_rate, new_weekly_rate)
            st.success('Employee added successfully!')
    
    # Main content area
    tab1, tab2 = st.tabs(['Employee List', 'Edit Deductions'])
    
    with tab1:
        df = payroll.get_employee_data()
        edited_df = st.data_editor(df, hide_index=True)
        
        # Update employee data if changed
        for idx, row in edited_df.iterrows():
            if row['ID'] in st.session_state.employees:
                payroll.update_employee(
                    row['ID'],
                    row['Name'],
                    row['Daily Rate'],
                    row['Weekly Rate']
                )
    
    with tab2:
        employee_id = st.selectbox('Select Employee', options=list(st.session_state.employees.keys()))
        if employee_id:
            emp = st.session_state.employees[employee_id]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cash_advance = st.number_input('Cash Advance', 
                    value=float(emp['deductions']['cash_advance']))
            with col2:
                snacks = st.number_input('Snacks', 
                    value=float(emp['deductions']['snacks']))
            with col3:
                sss_share = st.number_input('SSS Share', 
                    value=float(emp['deductions']['sss_share']))
            
            if st.button('Update Deductions'):
                emp['deductions']['cash_advance'] = Decimal(str(cash_advance))
                emp['deductions']['snacks'] = Decimal(str(snacks))
                emp['deductions']['sss_share'] = Decimal(str(sss_share))
                st.success('Deductions updated!')

if __name__ == '__main__':
    main()