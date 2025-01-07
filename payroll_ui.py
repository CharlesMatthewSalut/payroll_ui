import streamlit as st
import pandas as pd
from decimal import Decimal
import json
import os

class PayrollSystem:
    def __init__(self):
        self.data_file = 'payroll_data.json'
        self.load_data()
        self.overtime_rate = Decimal('100')
    
    def load_data(self):
        if 'employees' not in st.session_state:
            st.session_state.employees = {}
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for emp_id, emp_data in data.items():
                        self.add_employee(
                            int(emp_id),
                            emp_data['name'],
                            float(emp_data['daily_rate']),
                            float(emp_data['weekly_rate']),
                            save=False
                        )
                        emp = st.session_state.employees[int(emp_id)]
                        emp['overtime_hours'] = Decimal(str(emp_data['overtime_hours']))
                        for k, v in emp_data['deductions'].items():
                            emp['deductions'][k] = Decimal(str(v))
    
    def save_data(self):
        data = {}
        for emp_id, emp_data in st.session_state.employees.items():
            data[str(emp_id)] = {
                'name': emp_data['name'],
                'daily_rate': str(emp_data['daily_rate']),
                'weekly_rate': str(emp_data['weekly_rate']),
                'overtime_hours': str(emp_data['overtime_hours']),
                'deductions': {k: str(v) for k, v in emp_data['deductions'].items()}
            }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_employee(self, id, name, daily_rate, weekly_rate, save=True):
        if not name or daily_rate <= 0 or weekly_rate <= 0:
            return False
        
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
        if save:
            self.save_data()
        return True

    def update_employee(self, id, name, daily_rate, weekly_rate, overtime_hours, deductions):
        if id in st.session_state.employees:
            st.session_state.employees[id].update({
                'name': name,
                'daily_rate': Decimal(str(daily_rate)),
                'weekly_rate': Decimal(str(weekly_rate)),
                'overtime_hours': Decimal(str(overtime_hours)),
                'deductions': {k: Decimal(str(v)) for k, v in deductions.items()}
            })
            self.save_data()
            return True
        return False

    def delete_employee(self, id):
        if id in st.session_state.employees:
            del st.session_state.employees[id]
            self.save_data()
            return True
        return False

def main():
    st.title('Payroll Management System')
    
    payroll = PayrollSystem()
    
    tab1, tab2, tab3 = st.tabs(['View/Delete', 'Add Employee', 'Edit Employee'])
    
    with tab1:
        if st.session_state.employees:
            data = []
            for id, emp in st.session_state.employees.items():
                data.append({
                    'ID': id,
                    'Name': emp['name'],
                    'Daily Rate': float(emp['daily_rate']),
                    'Weekly Rate': float(emp['weekly_rate']),
                    'Overtime Hours': float(emp['overtime_hours']),
                    'Total Deductions': sum(float(v) for v in emp['deductions'].values())
                })
            df = pd.DataFrame(data)
            st.dataframe(df)
            
            col1, col2 = st.columns(2)
            with col1:
                to_delete = st.selectbox('Select Employee to Delete', 
                    options=[f"{emp['name']} (ID: {id})" for id, emp in st.session_state.employees.items()])
            with col2:
                if st.button('Delete Employee', type='primary'):
                    id_to_delete = int(to_delete.split('ID: ')[1].rstrip(')'))
                    if payroll.delete_employee(id_to_delete):
                        st.success('Employee deleted successfully!')
                        st.rerun()
    
    with tab2:
        with st.form('add_employee'):
            st.header('Add New Employee')
            new_id = st.number_input('Employee ID', min_value=1, step=1)
            new_name = st.text_input('Name')
            new_daily_rate = st.number_input('Daily Rate', min_value=0.0)
            new_weekly_rate = st.number_input('Weekly Rate', min_value=0.0)
            
            if st.form_submit_button('Add Employee'):
                if new_id in st.session_state.employees:
                    st.error('Employee ID already exists!')
                elif payroll.add_employee(new_id, new_name, new_daily_rate, new_weekly_rate):
                    st.success('Employee added successfully!')
                    st.rerun()
                else:
                    st.error('Please fill all fields correctly!')
    
    with tab3:
        if st.session_state.employees:
            employee_id = st.selectbox('Select Employee to Edit', 
                options=[f"{emp['name']} (ID: {id})" for id, emp in st.session_state.employees.items()])
            id_to_edit = int(employee_id.split('ID: ')[1].rstrip(')'))
            emp = st.session_state.employees[id_to_edit]
            
            with st.form('edit_employee'):
                name = st.text_input('Name', value=emp['name'])
                daily_rate = st.number_input('Daily Rate', value=float(emp['daily_rate']))
                weekly_rate = st.number_input('Weekly Rate', value=float(emp['weekly_rate']))
                overtime_hours = st.number_input('Overtime Hours', value=float(emp['overtime_hours']))
                
                st.subheader('Deductions')
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
                
                deductions = {
                    'cash_advance': cash_advance,
                    'snacks': snacks,
                    'sss_share': sss_share
                }
                
                if st.form_submit_button('Update Employee'):
                    if payroll.update_employee(id_to_edit, name, daily_rate, weekly_rate, 
                                            overtime_hours, deductions):
                        st.success('Employee updated successfully!')
                        st.rerun()
        else:
            st.warning('No employees to edit')

if __name__ == '__main__':
    main()