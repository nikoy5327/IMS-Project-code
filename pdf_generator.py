from fpdf import FPDF

def generate_receipt(transaction, items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Carol's Distributors Receipt", ln=True)

    for i in items:
        pdf.cell(200, 10, txt=f"{i['name']} x{i['qty']} - ${i['price']}", ln=True)

    pdf.cell(200, 10, txt=f"Total: ${transaction.total}", ln=True)
    filename = f"receipt_{transaction.transaction_id}.pdf"
    pdf.output(filename)

    return filename
