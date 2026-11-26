import io
import csv
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.repositories.bill_repository import BillRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.employee_repository import EmployeeRepository


class ReportService:
    def __init__(self):
        self.bill_repo = BillRepository()
        self.inventory_repo = InventoryRepository()
        self.employee_repo = EmployeeRepository()

    # ---------------------------------------------------------------- CSV
    def sales_csv(self, start_dt, end_dt) -> str:
        bills = self.bill_repo.bills_between(start_dt, end_dt)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Bill No", "Date", "Cashier", "Customer", "Subtotal", "Discount", "Tax", "Total", "Payment Mode"])
        for b in bills:
            writer.writerow([
                b.bill_number,
                b.bill_date.strftime("%Y-%m-%d %H:%M"),
                b.cashier.full_name if b.cashier else "",
                b.customer.name if b.customer else "Walk-in",
                b.subtotal, b.discount_amount, b.tax_amount, b.grand_total, b.payment_mode,
            ])
        return buffer.getvalue()

    def inventory_csv(self) -> str:
        items = self.inventory_repo.get_all()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Ingredient", "Quantity", "Unit", "Minimum Stock", "Status"])
        for i in items:
            writer.writerow([i.name, i.quantity, i.unit, i.minimum_stock, i.stock_status])
        return buffer.getvalue()

    def employee_csv(self) -> str:
        employees = self.employee_repo.active_employees()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Employee ID", "Name", "Role", "Phone", "Salary", "Joining Date"])
        for e in employees:
            writer.writerow([e.id, e.name, e.role, e.phone, e.salary, e.joining_date])
        return buffer.getvalue()

    # ------------------------------------------------------------- Excel
    def sales_excel_bytes(self, start_dt, end_dt) -> bytes:
        bills = self.bill_repo.bills_between(start_dt, end_dt)
        df = pd.DataFrame([
            {
                "Bill No": b.bill_number,
                "Date": b.bill_date,
                "Customer": b.customer.name if b.customer else "Walk-in",
                "Subtotal": float(b.subtotal),
                "Discount": float(b.discount_amount),
                "Tax": float(b.tax_amount),
                "Total": float(b.grand_total),
                "Payment Mode": b.payment_mode,
            }
            for b in bills
        ])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            (df if not df.empty else pd.DataFrame(columns=["Bill No"])).to_excel(
                writer, index=False, sheet_name="Sales"
            )
        return buffer.getvalue()

    # --------------------------------------------------------------- PDF
    def daily_sales_pdf_bytes(self, report_date, restaurant_name="Smart Restaurant") -> bytes:
        start_dt = datetime.combine(report_date, datetime.min.time())
        end_dt = datetime.combine(report_date, datetime.max.time())
        bills = self.bill_repo.bills_between(start_dt, end_dt)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"<b>{restaurant_name}</b>", styles["Title"]),
            Paragraph(f"Daily Sales Report - {report_date.strftime('%d %B %Y')}", styles["Heading2"]),
            Spacer(1, 10),
        ]

        total_revenue = sum(float(b.grand_total) for b in bills)
        total_tax = sum(float(b.tax_amount) for b in bills)
        story.append(Paragraph(f"Total Bills: {len(bills)} | Total Revenue: {total_revenue:.2f} | Total Tax Collected: {total_tax:.2f}", styles["Normal"]))
        story.append(Spacer(1, 12))

        table_data = [["Bill No", "Time", "Customer", "Subtotal", "Discount", "Tax", "Total"]]
        for b in bills:
            table_data.append([
                b.bill_number,
                b.bill_date.strftime("%H:%M"),
                b.customer.name if b.customer else "Walk-in",
                f"{float(b.subtotal):.2f}",
                f"{float(b.discount_amount):.2f}",
                f"{float(b.tax_amount):.2f}",
                f"{float(b.grand_total):.2f}",
            ])
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F3E46")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ]))
        story.append(table)
        doc.build(story)
        return buffer.getvalue()

    def tax_report_pdf_bytes(self, start_date, end_date, restaurant_name="Smart Restaurant", gstin="") -> bytes:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        bills = self.bill_repo.bills_between(start_dt, end_dt)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"<b>{restaurant_name}</b> - GSTIN: {gstin}", styles["Title"]),
            Paragraph(f"Tax Report: {start_date} to {end_date}", styles["Heading2"]),
            Spacer(1, 10),
        ]
        total_tax = sum(float(b.tax_amount) for b in bills)
        total_sales = sum(float(b.grand_total) for b in bills)
        story.append(Paragraph(f"Total Taxable Sales: {total_sales:.2f}", styles["Normal"]))
        story.append(Paragraph(f"Total Tax Collected: {total_tax:.2f}", styles["Normal"]))
        doc.build(story)
        return buffer.getvalue()
