import streamlit as st
import pandas as pd
from decimal import Decimal
import json
import os
from datetime import datetime, timedelta


class PayrollSystem:
    def __init__(self):
        self.data_file = 'payroll_data.json'
        self.overtime_rate = Decimal('100')
        self.load_data()

    def load_data(self):
        if 'employees' not in st.session_state:
            st.session_state.employees = {}
            if os.path.exists(self.data_file):
                try:
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
                            emp['overtime_hours'] = {k: Decimal(str(v)) for k, v in emp_data.get('overtime_hours', {}).items()}
                            emp['deductions'] = {k: Decimal(str(v)) for k, v in emp_data.get('deductions', {}).items()}
                except (FileNotFoundError, json.JSONDecodeError):
                    st.error("Error loading payroll data file.")

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                str(emp_id): {
                    'name': emp_data['name'],
                    'daily_rate': str(emp_data['daily_rate']),
                    'weekly_rate': str(emp_data['weekly_rate']),
                    'overtime_hours': {k: str(v) for k, v in emp_data['overtime_hours'].items()},
                    'deductions': {k: str(v) for k, v in emp_data['deductions'].items()}
                }
                for emp_id, emp_data in st.session_state.employees.items()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            st.error("Error saving payroll data.")

    def add_employee(self, id, name, daily_rate, weekly_rate, save=True):
        if not name or daily_rate <= 0 or weekly_rate <= 0:
            st.error("Invalid employee data.")
            return False

        st.session_state.employees[id] = {
            'name': name,
            'daily_rate': Decimal(str(daily_rate)),
            'weekly_rate': Decimal(str(weekly_rate)),
            'overtime_hours': {str(i): Decimal('0') for i in range(7)},
            'deductions': {
                'cash_advance': Decimal('0'),
                'snacks': Decimal('0'),
                'sss_share': Decimal('0')
            }
        }
        if save:
            self.save_data()
        return True

    def update_employee(self, id, field, value, day=None):
        if id in st.session_state.employees:
            emp = st.session_state.employees[id]
            if field == 'overtime':
                emp['overtime_hours'][str(day)] = Decimal(str(value))
            elif field in emp['deductions']:
                emp['deductions'][field] = Decimal(str(value))
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
    st.title('Weekly Payroll System')
    payroll = PayrollSystem()

    with st.sidebar:
        crud_action = st.radio("Select Action", ["View", "Add", "Edit", "Delete"])

        if crud_action == "Add":
            with st.form('add_employee'):
                st.subheader('Add New Employee')
                new_id = st.number_input('ID', min_value=1, step=1, key="new_id")
                new_name = st.text_input('Name', key="new_name")
                new_daily_rate = st.number_input('Daily Rate', min_value=0.0, key="new_daily_rate")
                new_weekly_rate = st.number_input('Weekly Rate', min_value=0.0, key="new_weekly_rate")

                if st.form_submit_button('Add'):
                    if new_id in st.session_state.employees:
                        st.error('ID already exists!')
                    elif payroll.add_employee(new_id, new_name, new_daily_rate, new_weekly_rate):
                        st.success('Employee added successfully!')
                        st.experimental_rerun()

        elif crud_action == "Delete":
            if st.session_state.employees:
                to_delete = st.selectbox(
                    'Select Employee to Delete',
                    options=[f"{emp['name']} (ID: {id})" for id, emp in st.session_state.employees.items()],
                    key="delete_select"
                )
                if st.button('Delete', type='primary', key="delete_btn"):
                    id_to_delete = int(to_delete.split('ID: ')[1].rstrip(')'))
                    if payroll.delete_employee(id_to_delete):
                        st.success('Employee deleted successfully!')
                        st.experimental_rerun()

        elif crud_action == "Edit":
            if st.session_state.employees:
                employee_id = st.selectbox(
                    'Select Employee to Edit',
                    options=[f"{emp['name']} (ID: {id})" for id, emp in st.session_state.employees.items()],
                    key="edit_select"
                )
                id_to_edit = int(employee_id.split('ID: ')[1].rstrip(')'))
                emp = st.session_state.employees[id_to_edit]

                st.subheader('Edit Deductions')
                for deduction_type in emp['deductions']:
                    new_value = st.number_input(
                        deduction_type.replace('_', ' ').title(),
                        value=float(emp['deductions'][deduction_type]),
                        key=f"edit_{deduction_type}"
                    )
                    if new_value != float(emp['deductions'][deduction_type]):
                        payroll.update_employee(id_to_edit, deduction_type, new_value)
                        st.experimental_rerun()

    if st.session_state.employees:
        week_dates = [(datetime.now() + timedelta(days=i)).strftime('%a\n%m/%d') for i in range(7)]
        data = []

        for id, emp in st.session_state.employees.items():
            row = {
                'ID': id,
                'Name': emp['name'],
                'Rate': float(emp['daily_rate'])
            }

            for i, date in enumerate(week_dates):
                row[date] = float(emp['overtime_hours'][str(i)])
                new_ot = st.number_input(
                    f"OT for {emp['name']} on {date}",
                    value=float(emp['overtime_hours'][str(i)]),
                    key=f"ot_{id}_{i}",
                    label_visibility="collapsed"
                )
                if new_ot != float(emp['overtime_hours'][str(i)]):
                    payroll.update_employee(id, 'overtime', new_ot, i)
                    st.experimental_rerun()

            for k, v in emp['deductions'].items():
                row[k.replace('_', ' ').title()] = float(v)

            data.append(row)

        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)


if __name__ == '__main__':
    main()
