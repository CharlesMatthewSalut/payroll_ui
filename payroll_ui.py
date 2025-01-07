import streamlit as st
import pandas as pd
from datetime import datetime
import xlsxwriter
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import base64

def calculate_overtime(hours, rate):
    """Calculate overtime pay"""
    if pd.isna(hours) or hours == 0:
        return 0
    return float(hours) * float(rate)

def generate_excel(data):
    """Generate Excel report"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Payroll', index=True)
    return output.getvalue()

def generate_pdf(employee_data, payroll_data):
    """Generate PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph(f"Payroll Report - {payroll_data['employee']}", styles['Title']))
    elements.append(Paragraph(f"Period: {payroll_data['start_date']} to {payroll_data['end_date']}", styles['Normal']))
    
    # Create payroll data table
    data = [
        ["Description", "Amount"],
        ["Weekly Rate", f"₱{payroll_data['weekly_rate']:,.2f}"],
        ["Overtime Pay", f"₱{payroll_data['overtime_pay']:,.2f}"],
        ["Deductions", f"₱{payroll_data['deductions']:,.2f}"],
        ["Final Pay", f"₱{payroll_data['final_pay']:,.2f}"]
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()

def create_payroll_system():
    st.title("Payroll Management System")
    
    # Initialize session states
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
    
    if 'attendance' not in st.session_state:
        st.session_state.attendance = {}
    
    if 'cash_advances' not in st.session_state:
        st.session_state.cash_advances = {}

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
    tab1, tab2, tab3, tab4 = st.tabs(["Employee Management", "Attendance Tracking", "Cash Advances", "Payroll Processing"])

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
        
        # Export employee data to Excel
        if st.button("Export Employee List"):
            excel_data = generate_excel(employee_df)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="employees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        st.subheader("Attendance Tracking")
        
        # Employee selection for attendance
        selected_emp_attendance = st.selectbox(
            "Select Employee",
            options=list(st.session_state.employees.keys()),
            key="attendance_employee"
        )
        
        # Date selection for attendance
        attendance_date = st.date_input("Date", key="attendance_date")
        
        # Attendance input
        col1, col2 = st.columns(2)
        with col1:
            time_in = st.time_input("Time In")
        with col2:
            time_out = st.time_input("Time Out")
            
        if st.button("Record Attendance"):
            if selected_emp_attendance not in st.session_state.attendance:
                st.session_state.attendance[selected_emp_attendance] = {}
            
            st.session_state.attendance[selected_emp_attendance][str(attendance_date)] = {
                'time_in': time_in.strftime("%H:%M"),
                'time_out': time_out.strftime("%H:%M")
            }
            st.success("Attendance recorded successfully!")
            
        # Display attendance records
        if selected_emp_attendance in st.session_state.attendance:
            st.write("Attendance Records")
            attendance_df = pd.DataFrame.from_dict(
                st.session_state.attendance[selected_emp_attendance],
                orient='index',
                columns=['time_in', 'time_out']
            )
            st.dataframe(attendance_df)

    with tab3:
        st.subheader("Cash Advances")
        
        # Employee selection for cash advance
        selected_emp_ca = st.selectbox(
            "Select Employee",
            options=list(st.session_state.employees.keys()),
            key="ca_employee"
        )
        
        # Cash advance input
        ca_amount = st.number_input("Cash Advance Amount", min_value=0.0)
        ca_date = st.date_input("Date", key="ca_date")
        
        if st.button("Record Cash Advance"):
            if selected_emp_ca not in st.session_state.cash_advances:
                st.session_state.cash_advances[selected_emp_ca] = {}
            
            st.session_state.cash_advances[selected_emp_ca][str(ca_date)] = ca_amount
            st.success("Cash advance recorded successfully!")
            
        # Display cash advance records
        if selected_emp_ca in st.session_state.cash_advances:
            st.write("Cash Advance Records")
            ca_df = pd.DataFrame.from_dict(
                st.session_state.cash_advances[selected_emp_ca],
                orient='index',
                columns=['amount']
            )
            st.dataframe(ca_df)

    with tab4:
        st.subheader("Payroll Processing")
        
        # Employee selection
        selected_employee = st.selectbox(
            "Select Employee",
            options=list(st.session_state.employees.keys()),
            key="payroll_employee"
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
            # Get total cash advances for the period
            total_ca = sum(st.session_state.cash_advances.get(selected_employee, {}).values())
            cash_advance = st.number_input("Cash Advance", min_value=0.0, value=total_ca)
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
            
            # Store payroll data for reports
            payroll_data = {
                'employee': selected_employee,
                'start_date': start_date,
                'end_date': end_date,
                'weekly_rate': employee_data['weekly_rate'],
                'overtime_pay': overtime_pay,
                'deductions': total_deductions,
                'final_pay': total_pay
            }
            
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
            
            # Generate reports
            # PDF Report
            pdf_report = generate_pdf(employee_data, payroll_data)
            st.download_button(
                label="Download PDF Report",
                data=pdf_report,
                file_name=f"payroll_report_{selected_employee}_{start_date}.pdf",
                mime="application/pdf"
            )
            
            # Excel Report
            payroll_df = pd.DataFrame([payroll_data])
            excel_report = generate_excel(payroll_df)
            st.download_button(
                label="Download Excel Report",
                data=excel_report,
                file_name=f"payroll_report_{selected_employee}_{start_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


if __name__ == "__main__":
    create_payroll_system()