import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.units import inch

def generate_company_report_pdf(data: Dict[str, Any], output_filepath: str) -> str:
    """
    Generate a PDF research report matching the Relu Consultancy format.
    """
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=0,  # Header banner at top
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Color tokens matching reference PDF image
    banner_bg = colors.HexColor("#0B0F19")      # Black banner background
    gold_accent = colors.HexColor("#D97706")    # Gold header accent
    section_gold = colors.HexColor("#B45309")   # Gold section title
    body_dark = colors.HexColor("#1F2937")      # Dark gray text
    border_gray = colors.HexColor("#E5E7EB")    # Divider gray

    title_banner_style = ParagraphStyle(
        "BannerSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#D1D5DB"),
        spaceAfter=4
    )

    title_main_style = ParagraphStyle(
        "BannerMain",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.white,
        spaceAfter=0
    )

    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=section_gold,
        spaceBefore=14,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=body_dark,
        spaceAfter=4
    )

    bold_label_style = ParagraphStyle(
        "BoldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=body_dark
    )

    story = []

    # 1. Top Header Banner
    company_name = data.get("company_name", "Company")
    banner_data = [
        [
            Paragraph("RELU CONSULTANCY · COMPANY RESEARCH REPORT", title_banner_style)
        ],
        [
            Paragraph(company_name, title_main_style)
        ]
    ]
    banner_table = Table(banner_data, colWidths=[7.2*inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), banner_bg),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('LINEBELOW', (0,1), (-1,1), 3, gold_accent),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))

    # 2. Company Information
    story.append(Paragraph("COMPANY INFORMATION", heading2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceAfter=8))
    
    info_data = [
        [
            Paragraph("Website", bold_label_style),
            Paragraph(str(data.get("website", "Not found")), body_style)
        ],
        [
            Paragraph("Phone", bold_label_style),
            Paragraph(str(data.get("phone_number", "Not publicly listed")), body_style)
        ],
        [
            Paragraph("Address", bold_label_style),
            Paragraph(str(data.get("address", "Not found in available sources.")), body_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 5.7*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Products & Services
    story.append(Paragraph("PRODUCTS & SERVICES", heading2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceAfter=8))
    prods = data.get("products_services", [])
    if prods and isinstance(prods, list):
        for prod in prods:
            story.append(Paragraph(f"• {prod}", body_style))
    else:
        story.append(Paragraph(str(prods) if prods else "Not found in available sources.", body_style))
    story.append(Spacer(1, 10))

    # 4. AI-Generated Pain Points
    story.append(Paragraph("AI-GENERATED PAIN POINTS", heading2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceAfter=8))
    pain_points = data.get("pain_points", [])
    if pain_points and isinstance(pain_points, list):
        for point in pain_points:
            story.append(Paragraph(f"• {point}", body_style))
    else:
        story.append(Paragraph(str(pain_points) if pain_points else "Not found in available sources.", body_style))
    story.append(Spacer(1, 10))

    # 5. Competitors
    story.append(Paragraph("COMPETITORS", heading2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_gray, spaceAfter=8))
    competitors = data.get("competitors", [])
    
    if competitors and isinstance(competitors, list):
        comp_data = []
        for comp in competitors:
            if isinstance(comp, dict):
                c_name = comp.get("name", "Competitor")
                c_site = comp.get("website", "")
            else:
                c_name = str(comp)
                c_site = ""
            comp_data.append([
                Paragraph(c_name, bold_label_style),
                Paragraph(c_site, body_style)
            ])

        comp_table = Table(comp_data, colWidths=[2.2*inch, 5.0*inch])
        comp_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(comp_table)
    else:
        story.append(Paragraph("Not found in available sources.", body_style))

    doc.build(story)
    return output_filepath
