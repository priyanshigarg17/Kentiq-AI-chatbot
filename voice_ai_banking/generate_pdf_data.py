# generate_pdf_data.py
# Auto-generated file

# ============================================================
#  generate_pdf_data.py — Dummy Bank Data PDF Generator
#  
#  PURPOSE:
#    Creates bank_dummy_data.pdf inside the /data folder.
#    The AI pulls account info, transaction history, transfer
#    rules, and KYC requirements from this PDF at runtime.
#
#  RUN ONCE:
#    python generate_pdf_data.py
# ============================================================

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def build_styles():
    """Define all paragraph styles used in the PDF."""
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "KentiqTitle",
        parent=base["Title"],
        fontSize=22,
        textColor=colors.HexColor("#C8963E"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "KentiqHeading",
        parent=base["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#1a2240"),
        spaceBefore=14,
        spaceAfter=6,
        borderPad=4,
    )
    subheading_style = ParagraphStyle(
        "KentiqSub",
        parent=base["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#C8963E"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "KentiqBody",
        parent=base["Normal"],
        fontSize=10,
        leading=16,
        spaceAfter=4,
    )
    return title_style, heading_style, subheading_style, body_style


def build_table(data, col_widths=None):
    """Helper — creates a styled reportlab Table."""
    tbl = Table(data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1a2240")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    return tbl


def generate_pdf(output_path: str = "data/bank_dummy_data.pdf"):
    """Main function — builds and saves the bank data PDF."""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    T, H, SH, B = build_styles()
    story = []

    # ── COVER
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("KENTIQ AI VOICE BANKING ASSISTANT", T))
    story.append(Paragraph("Dubai Bank — Mock Data & Workflow Reference", T))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#C8963E")))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "This document contains all dummy bank data and mock workflows used by the "
        "Kentiq AI Voice Bot. The backend PDF reader module extracts this information "
        "at runtime to power voice responses.", B
    ))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 1 — CUSTOMER ACCOUNTS
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 1: Customer Accounts", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("1.1 Primary Account", SH))
    primary_data = [
        ["Field", "Value"],
        ["Account Holder", "Ahmed Al Mansouri"],
        ["Account Number (Masked)", "****3456"],
        ["Full IBAN", "AE070331234567890123456"],
        ["Account Type", "Current Account"],
        ["Currency", "AED (UAE Dirham)"],
        ["Available Balance", "AED 48,250.75"],
        ["Total Balance", "AED 48,250.75"],
        ["Overdraft Limit", "AED 10,000.00"],
        ["Account Status", "Active"],
        ["Branch", "Dubai Main Branch"],
        ["Opened On", "15 March 2019"],
    ]
    story.append(build_table(primary_data, col_widths=[7 * cm, 10 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1.2 Savings Account", SH))
    savings_data = [
        ["Field", "Value"],
        ["Account Holder", "Ahmed Al Mansouri"],
        ["Account Number (Masked)", "****3789"],
        ["Full IBAN", "AE070331234567890123789"],
        ["Account Type", "Savings Account"],
        ["Currency", "AED (UAE Dirham)"],
        ["Available Balance", "AED 1,25,000.00"],
        ["Interest Rate", "2.5% per annum"],
        ["Account Status", "Active"],
        ["Branch", "Dubai Main Branch"],
        ["Opened On", "10 June 2020"],
    ]
    story.append(build_table(savings_data, col_widths=[7 * cm, 10 * cm]))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 2 — TRANSACTION HISTORY
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 2: Recent Transaction History", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Last 10 transactions for Primary Account (****3456):", B
    ))

    txn_data = [
        ["Date", "Description", "Type", "Amount (AED)", "Balance After"],
        ["24 Apr 2025", "Salary Credit — Kentiq Corp", "Credit", "+15,000.00", "48,250.75"],
        ["23 Apr 2025", "ADNOC Fuel Station", "Debit", "-200.00", "33,250.75"],
        ["22 Apr 2025", "Carrefour Hypermarket", "Debit", "-450.50", "33,450.75"],
        ["20 Apr 2025", "Dubai Electricity Bill", "Debit", "-650.00", "33,901.25"],
        ["18 Apr 2025", "Online Transfer — Ravi Kumar", "Debit", "-5,000.00", "34,551.25"],
        ["15 Apr 2025", "ATM Withdrawal", "Debit", "-1,000.00", "39,551.25"],
        ["12 Apr 2025", "Amazon.ae Purchase", "Debit", "-299.00", "40,551.25"],
        ["10 Apr 2025", "Rent Credit Reversal", "Credit", "+3,000.00", "40,850.25"],
        ["08 Apr 2025", "Noon Online Shopping", "Debit", "-178.50", "37,850.25"],
        ["05 Apr 2025", "Interest Credit", "Credit", "+250.00", "38,028.75"],
    ]
    story.append(build_table(txn_data, col_widths=[3*cm, 5.5*cm, 2*cm, 3*cm, 3.5*cm]))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 3 — MONEY TRANSFER WORKFLOWS
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 3: Money Transfer Mock Workflows", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("3.1 Transfer Limits", SH))
    limits_data = [
        ["Transfer Type", "Min Amount (AED)", "Max Amount (AED)", "Processing Time"],
        ["Within Dubai Bank", "10", "5,00,000", "Instant"],
        ["Local Bank Transfer (UAEFTS)", "10", "2,00,000", "Same Day"],
        ["International Wire (SWIFT)", "100", "1,00,000", "1-3 Business Days"],
        ["Mobile Pay", "10", "10,000", "Instant"],
    ]
    story.append(build_table(limits_data, col_widths=[5*cm, 3.5*cm, 3.5*cm, 5*cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("3.2 Sample Transfer Confirmation Flow", SH))
    flow_steps = [
        ["Step", "Bot Prompt", "User Response (Example)"],
        ["1", "Please say the name of the beneficiary.", "Ravi Kumar"],
        ["2", "Which bank should I transfer to?", "HDFC Bank"],
        ["3", "Please say the beneficiary's account number.", "1234 5678 9012"],
        ["4", "How much would you like to transfer in AED?", "Five hundred"],
        ["5", "Shall I proceed? Say Yes to confirm or No to cancel.", "Yes"],
        ["6", "Transfer of AED 500 to Ravi Kumar completed. Ref: TXN84521.", "—"],
    ]
    story.append(build_table(flow_steps, col_widths=[1.5*cm, 7*cm, 8.5*cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("3.3 Registered Beneficiaries", SH))
    bene_data = [
        ["Name", "Bank", "Account (Masked)", "Currency", "Relation"],
        ["Ravi Kumar", "HDFC Bank, India", "****9012", "INR", "Friend"],
        ["Sara Al Ali", "Emirates NBD", "****4521", "AED", "Sister"],
        ["John Smith", "Barclays UK", "****7823", "GBP", "Business"],
        ["Fatima Hassan", "Dubai Islamic Bank", "****3301", "AED", "Colleague"],
    ]
    story.append(build_table(bene_data, col_widths=[4*cm, 4.5*cm, 3.5*cm, 2.5*cm, 2.5*cm]))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 4 — CHEQUE VERIFICATION RULES
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 4: Cheque Verification Rules", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("4.1 Valid Cheque Criteria", SH))
    cheque_rules = [
        ["Rule #", "Validation Rule", "Action on Fail"],
        ["1", "File must be JPG, PNG, or WEBP", "Reject with voice feedback"],
        ["2", "File size must be less than 5 MB", "Reject with voice feedback"],
        ["3", "Image must be at least 800x400 pixels", "Warn user, request clearer image"],
        ["4", "Image must contain MICR line (bottom strip)", "Mark as suspicious"],
        ["5", "Cheque date must not be more than 6 months old", "Reject as stale cheque"],
        ["6", "Payee name must be legible", "Request re-upload"],
        ["7", "Amount in words and figures must match", "Flag for manual review"],
    ]
    story.append(build_table(cheque_rules, col_widths=[1.5*cm, 8*cm, 7.5*cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("4.2 Voice Commands for Cheque", SH))
    cmd_data = [
        ["Voice Command", "System Response"],
        ["Upload cheque", "Prompts user to upload cheque image file"],
        ["Scan cheque", "Activates camera (if available) or file upload"],
        ["Verify cheque", "Runs validation on already-uploaded image"],
        ["Cancel", "Aborts cheque verification flow"],
    ]
    story.append(build_table(cmd_data, col_widths=[6*cm, 11*cm]))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 5 — KYC WORKFLOWS
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 5: Voice KYC Workflows", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("5.1 KYC Process Steps", SH))
    kyc_data = [
        ["Step", "Action", "Duration", "Storage"],
        ["1", "User says 'Start KYC'", "—", "—"],
        ["2", "Bot confirms: 'KYC started. Please look at camera.'", "—", "—"],
        ["3", "System records 5-second audio clip", "5 seconds", "kyc_recordings/<KYC_ID>.wav"],
        ["4", "System records 10-second video clip (if camera available)", "10 seconds", "kyc_recordings/<KYC_ID>.mp4"],
        ["5", "Bot confirms completion with KYC reference ID", "—", "—"],
        ["6", "Files saved locally for manual review", "—", "Local filesystem"],
    ]
    story.append(build_table(kyc_data, col_widths=[1.5*cm, 6*cm, 2.5*cm, 7*cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("5.2 KYC Documents Required (Dummy)", SH))
    doc_data = [
        ["Document", "Format", "Status for Ahmed Al Mansouri"],
        ["Emirates ID", "Image / PDF", "Verified"],
        ["Passport Copy", "Image / PDF", "Verified"],
        ["Proof of Address", "PDF", "Pending"],
        ["Selfie with ID", "Image", "Pending"],
        ["Voice Sample", "WAV / MP3", "To be recorded"],
        ["Video Sample", "MP4", "To be recorded"],
    ]
    story.append(build_table(doc_data, col_widths=[5*cm, 4*cm, 8*cm]))
    story.append(PageBreak())

    # ─────────────────────────────────────────
    # SECTION 6 — ERROR HANDLING SCRIPTS
    # ─────────────────────────────────────────
    story.append(Paragraph("SECTION 6: Error Handling Voice Scripts", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    story.append(Spacer(1, 0.3 * cm))

    err_data = [
        ["Error Type", "Voice Response Script"],
        ["No speech detected", "I did not hear anything. Please speak clearly and try again."],
        ["Unclear speech", "Sorry, I could not understand that. Please repeat slowly."],
        ["Background noise", "There seems to be background noise. Please move to a quieter area."],
        ["Unknown intent", "I am not sure what you mean. You can say: Balance, Transfer, Cheque, KYC, or Help."],
        ["Microphone error", "I am having trouble accessing your microphone. Please check permissions."],
        ["Network error", "I am unable to process your request right now. Please try again in a moment."],
        ["Timeout", "You have not responded for a while. Returning to main menu."],
        ["Invalid file", "The file you uploaded is not valid. Please upload a JPG or PNG image under 5 MB."],
        ["Transfer limit exceeded", "Transfer amount exceeds your daily limit. Please try a lower amount."],
    ]
    story.append(build_table(err_data, col_widths=[5*cm, 12*cm]))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("SECTION 7: Supported Voice Commands — Full List", H))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a2240")))
    cmds = [
        ["Command Category", "Example Phrases", "Intent Triggered"],
        ["Balance", "Check balance / How much money do I have / Account balance", "BALANCE"],
        ["Transfer", "Transfer money / Send money / Pay someone / Wire transfer", "TRANSFER"],
        ["Cheque", "Upload cheque / Scan cheque / Verify cheque", "CHEQUE"],
        ["KYC", "Start KYC / Begin verification / Identity check", "KYC"],
        ["Confirm", "Yes / Confirm / Proceed / Okay / Sure", "CONFIRM"],
        ["Cancel", "No / Cancel / Stop / Abort", "CANCEL"],
        ["Help", "Help / What can you do / Show options / Menu", "HELP"],
    ]
    story.append(build_table(cmds, col_widths=[4*cm, 8*cm, 5*cm]))

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#C8963E")))
    story.append(Paragraph(
        "End of Kentiq AI Voice Banking Assistant — Bank Data Reference PDF", B
    ))

    doc.build(story)
    print(f"[PDF] Bank data PDF created at: {output_path}")


if __name__ == "__main__":
    generate_pdf(output_path="data/bank_dummy_data.pdf")