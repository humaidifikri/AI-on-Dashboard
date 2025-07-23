from fpdf import FPDF
import base64
import textwrap
import os
import tempfile
from datetime import datetime

class HealthInsightPDF(FPDF):
    def header(self):
        # Logo atau header (opsional - bisa ditambah logo jika ada)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(41, 128, 185)  # Warna biru
        self.cell(0, 10, 'Health Insight Report', 0, 1, 'C')
        self.set_text_color(0, 0, 0)  # Kembali ke hitam
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%d %B %Y")} - Page {self.page_no()}', 0, 0, 'C')

def clean_text_for_pdf(text):
    """Hapus emoji, tag XML/HTML, dan karakter yang tidak didukung FPDF"""
    import re
    
    # Hapus tag XML/HTML seperti <think>, </think>, dll
    text = re.sub(r'<[^>]+>', '', text)
    
    # Hapus bagian thinking yang mungkin bocor dari AI
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Dictionary untuk replace emoji dengan text
    emoji_replacements = {
        '🧠': '[AI]',
        '💡': '[TIP]',
        '📊': '[DATA]',
        '⚠️': '[!]',
        '✅': '[OK]',
        '❌': '[X]',
        '📈': '[NAIK]',
        '📉': '[TURUN]',
        '🏥': '[KESEHATAN]',
        '🎯': '[TARGET]',
        '⭐': '[STAR]',
        '💪': '[KUAT]',
        '🏃': '[LARI]',
        '🥗': '[SEHAT]',
        '⏰': '[WAKTU]',
        '📝': '[CATATAN]',
        '🔥': '[PANAS]',
    }
    
    # Replace emoji dengan text
    for emoji, replacement in emoji_replacements.items():
        text = text.replace(emoji, replacement)
    
    # Hapus karakter Unicode lainnya yang mungkin bermasalah
    # Hanya biarkan karakter ASCII dan beberapa karakter Latin
    cleaned_text = ''
    for char in text:
        if ord(char) < 256:  # ASCII dan Latin-1
            cleaned_text += char
        else:
            cleaned_text += '?'  # Replace dengan placeholder
    
    # Hapus whitespace berlebihan dan baris kosong berturut-turut
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)  # Max 2 newlines
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text
def generate_pdf(insight_text):
    # Clean text dari emoji dan karakter Unicode
    insight_text = clean_text_for_pdf(insight_text)
    
    pdf = HealthInsightPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Tambahkan judul utama
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 15, "ANALISIS KESEHATAN DARI AI", ln=True, align='C')
    pdf.ln(5)
    
    # Tambahkan garis pembatas
    pdf.set_draw_color(52, 152, 219)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)
    
    # Set font untuk konten
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    
    # Proses teks insight
    lines = insight_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        # Deteksi poin-poin (dimulai dengan angka atau bullet)
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')):
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(41, 128, 185)
            
            # Wrap teks untuk poin
            wrapped_lines = textwrap.wrap(line, width=85)
            for i, wrapped_line in enumerate(wrapped_lines):
                if i == 0:
                    pdf.cell(10, 8, ">>", 0, 0, 'C')  # Ganti bullet dengan >>
                    pdf.cell(0, 8, wrapped_line[2:] if line.startswith(('1.', '2.', '3.', '4.', '5.')) else wrapped_line, 0, 1)
                else:
                    pdf.cell(10, 8, "", 0, 0)
                    pdf.cell(0, 8, wrapped_line, 0, 1)
            
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)
            
        # Deteksi heading atau judul (huruf besar semua atau dengan **bold**)
        elif line.isupper() or (line.startswith('**') and line.endswith('**')):
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(231, 76, 60)
            clean_line = line.replace('**', '')
            pdf.cell(0, 10, clean_line, ln=True)
            pdf.ln(2)
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(0, 0, 0)
            
        else:
            # Teks biasa
            wrapped_lines = textwrap.wrap(line, width=85)
            for wrapped_line in wrapped_lines:
                pdf.cell(0, 7, wrapped_line, ln=True)
            pdf.ln(1)
    
    # Tambahkan kotak kesimpulan di akhir
    pdf.ln(10)
    pdf.set_draw_color(46, 204, 113)
    pdf.set_fill_color(230, 247, 236)
    pdf.rect(15, pdf.get_y(), 180, 25, 'DF')
    
    pdf.set_xy(20, pdf.get_y() + 5)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(39, 174, 96)
    pdf.cell(0, 6, "[TIP] Catatan:", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Konsultasikan dengan dokter atau ahli gizi untuk saran yang lebih personal.", ln=True)
    
    # Buat file temporary dengan nama unik
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix='insight_') as temp_file:
        output_path = temp_file.name
    
    pdf.output(output_path)
    return output_path

def get_download_link(file_path, label):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode()
        
        # Hapus file temporary setelah dibaca
        os.unlink(file_path)
        
        # Get filename dari path untuk download
        filename = f"health_insight_{datetime.now().strftime('%Y/%m/%d')}.pdf"
        
        # Styling untuk tombol download
        href = f'''
        <div style="text-align: center; margin: 20px 0;">
            <a href="data:application/pdf;base64,{base64_pdf}" 
               download="{filename}" 
               style="
                   background: linear-gradient(45deg, #3498db, #2980b9);
                   color: white;
                   padding: 12px 24px;
                   text-decoration: none;
                   border-radius: 8px;
                   font-weight: bold;
                   box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                   display: inline-block;
                   transition: all 0.3s ease;
               "
               onmouseover="this.style.transform='translateY(-2px)'"
               onmouseout="this.style.transform='translateY(0px)'">
                {label}
            </a>
        </div>
        '''
        return href
        
    except Exception as e:
        # Jika ada error, tetap coba hapus file
        if os.path.exists(file_path):
            os.unlink(file_path)
        return f"<p>Error creating download link: {str(e)}</p>"