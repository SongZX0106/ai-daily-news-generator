from PyQt5.QtWidgets import QFileDialog
from docx import Document
from reportlab.pdfgen import canvas

def export_report(text):
    path, _ = QFileDialog.getSaveFileName(None, "导出文件", "", "Text Files (*.txt);;Markdown (*.md);;Word (*.docx);;PDF (*.pdf)")
    if path.endswith(".txt") or path.endswith(".md"):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    elif path.endswith(".docx"):
        doc = Document()
        doc.add_paragraph(text)
        doc.save(path)
    elif path.endswith(".pdf"):
        c = canvas.Canvas(path)
        for i, line in enumerate(text.split("\n")):
            c.drawString(50, 800 - i * 15, line)
        c.save()