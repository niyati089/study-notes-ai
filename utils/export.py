# utils/export.py (UPDATED VERSION - replace your existing file)
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import json
from datetime import datetime

def export_text_to_pdf(text, filename="answer.pdf"):
    """Export simple text to PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add content
    for para in text.split('\n'):
        if para.strip():
            story.append(Paragraph(para, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    buffer.seek(0)
    
    with open(filename, 'wb') as f:
        f.write(buffer.read())
    
    return filename


def export_notes_to_pdf(notes, filename="my_notes.pdf"):
    """
    Export all notes to a beautiful PDF with styling
    notes: list of tuples (id, title, content, created_at)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#AF52DE'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Note title style
    note_title_style = ParagraphStyle(
        'NoteTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#007AFF'),
        spaceAfter=10,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Date style
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        spaceAfter=10,
        fontName='Helvetica-Oblique'
    )
    
    # Content style
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=20,
        leftIndent=10,
        fontName='Helvetica'
    )
    
    story = []
    
    # Header
    story.append(Paragraph("📚 My Study Notes", title_style))
    story.append(Paragraph(f"Exported on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add separator line
    story.append(Table([['']], colWidths=[6.5*inch], style=[
        ('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#AF52DE')),
    ]))
    story.append(Spacer(1, 0.2*inch))
    
    # Add each note
    for i, (nid, title, content, created) in enumerate(notes, 1):
        # Note number and title
        story.append(Paragraph(f"{i}. {title}", note_title_style))
        
        # Date
        story.append(Paragraph(f"Created: {created}", date_style))
        
        # Content
        # Split content into paragraphs
        for para in content.split('\n'):
            if para.strip():
                story.append(Paragraph(para, content_style))
        
        # Add some space between notes
        story.append(Spacer(1, 0.3*inch))
        
        # Add separator between notes (not after last one)
        if i < len(notes):
            story.append(Table([['']], colWidths=[6.5*inch], style=[
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.lightgrey),
            ]))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    with open(filename, 'wb') as f:
        f.write(buffer.read())
    
    return filename


def export_flashcards_to_pdf(flashcards, filename="my_flashcards.pdf"):
    """
    Export flashcards to a beautiful PDF with card-style layout
    flashcards: list of tuples (id, front, back, tags, created_at)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF2D55'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Card question style
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=13,
        textColor=colors.HexColor('#007AFF'),
        fontName='Helvetica-Bold',
        leading=18
    )
    
    # Card answer style
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#34C759'),
        leading=16,
        fontName='Helvetica'
    )
    
    # Date style
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        spaceAfter=10,
        fontName='Helvetica-Oblique'
    )
    
    story = []
    
    # Header
    story.append(Paragraph("🎴 My Flashcards", title_style))
    story.append(Paragraph(f"Exported on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
    story.append(Paragraph(f"Total Cards: {len(flashcards)}", date_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add each flashcard as a styled card
    for i, (fid, front, back, tags, created) in enumerate(flashcards, 1):
        # Truncate very long text to prevent layout errors
        front_text = front[:500] + "..." if len(front) > 500 else front
        back_text = back[:800] + "..." if len(back) > 800 else back
        
        # Create a table for the card with colored background
        card_data = [
            [Paragraph(f"<b>Card {i}</b>", styles['Normal'])],
            [Paragraph(f"❓ Question:", question_style)],
            [Paragraph(front_text, question_style)],
            [Paragraph(f"✅ Answer:", answer_style)],
            [Paragraph(back_text, answer_style)],
        ]
        
        if tags:
            card_data.append([Paragraph(f"🏷️ Tags: {tags[:100]}", date_style)])
        
        card_table = Table(card_data, colWidths=[6*inch])
        card_table.setStyle(TableStyle([
            # Background colors
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6E6FA')),  # Header
            ('BACKGROUND', (0, 1), (-1, 2), colors.HexColor('#F0F8FF')),  # Question
            ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#F0FFF0')),  # Answer
            
            # Borders
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#AF52DE')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#AF52DE')),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.lightgrey),
            
            # Padding
            ('PADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(card_table)
        story.append(Spacer(1, 0.25*inch))
        
        # Page break after every 2 cards (changed from 3 to prevent overflow)
        if i % 2 == 0 and i < len(flashcards):
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    with open(filename, 'wb') as f:
        f.write(buffer.read())
    
    return filename


# def export_notes_to_markdown(notes, filename="my_notes.md"):
#     """
#     Export notes to Markdown format
#     """
#     with open(filename, 'w', encoding='utf-8') as f:
#         f.write("# 📚 My Study Notes\n\n")
#         f.write(f"*Exported on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n")
#         f.write("---\n\n")
        
#         for i, (nid, title, content, created) in enumerate(notes, 1):
#             f.write(f"## {i}. {title}\n\n")
#             f.write(f"*Created: {created}*\n\n")
#             f.write(f"{content}\n\n")
#             f.write("---\n\n")
    
#     return filename


# def export_flashcards_to_json(flashcards, filename="my_flashcards.json"):
#     """
#     Export flashcards to JSON format (great for importing to other apps)
#     """
#     cards_list = []
#     for fid, front, back, tags, created in flashcards:
#         cards_list.append({
#             "id": fid,
#             "front": front,
#             "back": back,
#             "tags": tags.split(',') if tags else [],
#             "created_at": created
#         })
    
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump({
#             "exported_at": datetime.now().isoformat(),
#             "total_cards": len(cards_list),
#             "cards": cards_list
#         }, f, indent=2, ensure_ascii=False)
    
#     return filename


# def export_flashcards_to_anki(flashcards, filename="my_flashcards_anki.txt"):
#     """
#     Export flashcards in Anki-compatible format (tab-separated)
#     Can be imported directly into Anki
#     """
#     with open(filename, 'w', encoding='utf-8') as f:
#         for fid, front, back, tags, created in flashcards:
#             # Anki format: front\tback\ttags
#             f.write(f"{front}\t{back}\t{tags if tags else ''}\n")
    
#     return filename