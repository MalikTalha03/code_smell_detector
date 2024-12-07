import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json
import tempfile
import threading
from main import detect_code_smells_in_directory, analyze_code_snippet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors

class CodeSmellDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f4f4f9')

        # Style Configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f4f4f9')
        self.style.configure('TLabel', background='#f4f4f9', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12))

        # Create Main Layout
        self.create_main_layout()

        # Abbreviations for code smells
        self.ABBREVIATIONS = {
            "Long Parameter List": "LPL",
            "Long Base Class List": "LBCL",
            "Large Class": "LC",
            "Long Method": "LM",
            "Complex Container Comprehension": "CCC",
            "Long Lambda Function": "LLF",
            "Long Ternary Conditional Expression": "LTCE",
            "Long Scope Chaining": "LSC"
        }

        # Current report tracking
        self.current_report = None

    def create_main_layout(self):
        # Main Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Left Section - Code Input
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="Analyze Code Snippet", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Code Input Text Area
        self.code_input = tk.Text(left_frame, height=13, width=50, font=('Courier New', 10))
        self.code_input.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Bind event to enable/disable Analyze Code Button
        self.code_input.bind('<KeyRelease>', self.toggle_analyze_code_button)

        # Analyze Code Button
        self.analyze_code_btn = ttk.Button(left_frame, text="Analyze Code", command=self.analyze_code_snippet, state=tk.DISABLED)
        self.analyze_code_btn.pack(pady=10)

        # Right Section - File/Folder Upload
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)

        # Single File Upload
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(file_frame, text="Upload Python File", font=('Arial', 12)).pack()
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=30)
        file_entry.pack(side=tk.LEFT, padx=5)
        
        file_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        file_btn.pack(side=tk.LEFT)

        # Bind event to enable/disable Analyze File Button
        self.file_path.trace_add('write', self.toggle_analyze_file_button)
        self.analyze_file_btn = ttk.Button(file_frame, text="Analyze File", command=self.analyze_file, state=tk.DISABLED)
        self.analyze_file_btn.pack(side=tk.LEFT, padx=5)

        # Project Folder Upload
        folder_frame = ttk.Frame(right_frame)
        folder_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(folder_frame, text="Upload Project Folder", font=('Arial', 12)).pack()
        self.folder_path = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=30)
        folder_entry.pack(side=tk.LEFT, padx=5)
        
        folder_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        folder_btn.pack(side=tk.LEFT)

        # Bind event to enable/disable Scan Folder Button
        self.folder_path.trace_add('write', self.toggle_scan_folder_button)
        self.scan_folder_btn = ttk.Button(folder_frame, text="Scan Folder", command=self.scan_project, state=tk.DISABLED)
        self.scan_folder_btn.pack(side=tk.LEFT, padx=5)

        # Results Section
        results_frame = ttk.Frame(self.root)
        results_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Download PDF Button
        self.download_btn = ttk.Button(results_frame, text="Download PDF Report", command=self.download_pdf, state=tk.DISABLED)
        self.download_btn.pack(pady=10)

        # Chart and Summary
        self.chart_frame = ttk.Frame(results_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        # Total Smells Container
        self.total_smells_frame = ttk.Frame(results_frame)
        self.total_smells_frame.pack(fill=tk.X, pady=10)

    def toggle_analyze_code_button(self, event=None):
        # Enable Analyze Code button only when there's text in the input
        code = self.code_input.get("1.0", tk.END).strip()
        self.analyze_code_btn.config(state=tk.NORMAL if code else tk.DISABLED)

    def toggle_analyze_file_button(self, *args):
        # Enable Analyze File button only when a file is selected
        file_path = self.file_path.get()
        self.analyze_file_btn.config(state=tk.NORMAL if file_path else tk.DISABLED)

    def toggle_scan_folder_button(self, *args):
        # Enable Scan Folder button only when a folder is selected
        folder_path = self.folder_path.get()
        self.scan_folder_btn.config(state=tk.NORMAL if folder_path else tk.DISABLED)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        self.file_path.set(filename)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        self.folder_path.set(folder)

    def analyze_code_snippet(self):
        # Run analysis in a separate thread to prevent UI freezing
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter a code snippet")
            return

        def run_analysis():
            try:
                results = analyze_code_snippet(code)
                # Use root.after to ensure UI updates happen in main thread
                self.root.after(0, lambda: self.display_results(results))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=run_analysis).start()

    def analyze_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a Python file")
            return

        def run_analysis():
            try:
                with open(file_path, 'r') as file:
                    file_content = file.read()
                results = analyze_code_snippet(file_content, file_path)
                # Use root.after to ensure UI updates happen in main thread
                self.root.after(0, lambda: self.display_results(results))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=run_analysis).start()

    def scan_project(self):
        folder_path = self.folder_path.get()
        if not folder_path:
            messagebox.showwarning("Warning", "Please select a project folder")
            return

        def run_analysis():
            try:
                # Create a temporary JSON report
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_report.json') as temp_report:
                    report_filename = temp_report.name

                detect_code_smells_in_directory(folder_path, report_filename)
                
                # Load the report
                with open(report_filename, 'r') as report_file:
                    results = json.load(report_file)
                
                # Clean up temporary file
                os.unlink(report_filename)

                # Display results in main thread
                self.root.after(0, lambda: self.display_results(results))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=run_analysis).start()

    def display_results(self, data):
        # Clear previous chart and summary
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        for widget in self.total_smells_frame.winfo_children():
            widget.destroy()

        # Summarize code smells by type
        smell_counts = {}
        for item in data:
            smell = self.get_smell_abbreviation(item['code_smell'])
            smell_counts[smell] = smell_counts.get(smell, 0) + 1

        # Create Matplotlib Figure
        fig, ax = plt.subplots(figsize=(8, 4))
        smells = list(smell_counts.keys())
        counts = list(smell_counts.values())

        ax.bar(smells, counts, color='#007bff')
        ax.set_title('Code Smells Distribution')
        ax.set_xlabel('Code Smell Type')
        ax.set_ylabel('Number of Code Smells')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Embed Matplotlib chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Create summary cards for each smell type
        for smell, count in smell_counts.items():
            card_frame = ttk.Frame(self.total_smells_frame, style='TFrame')
            card_frame.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(card_frame, text=smell, font=('Arial', 12, 'bold')).pack()
            ttk.Label(card_frame, text=f"{count} smells", font=('Arial', 10)).pack()

        # Store the report for potential PDF download
        self.current_report = data

        # Enable Download PDF button
        self.download_btn.config(state=tk.NORMAL)

    # Existing methods remain unchanged
    def get_smell_abbreviation(self, full_smell_name):
        # Find the abbreviation for the full smell name
        for full_name, abbr in self.ABBREVIATIONS.items():
            if full_name.lower() in full_smell_name.lower():
                return abbr
        return full_smell_name  # Return original if no match found

    def download_pdf(self):
        if not self.current_report:
            messagebox.showwarning("Warning", "No report available to download")
            return

        # Ask user where to save the PDF
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not pdf_path:
            return

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        # Title
        styles = getSampleStyleSheet()
        title = Paragraph("Code Smell Detection Report", styles['Title'])
        elements.append(title)

        # Add spacing
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # Abbreviations Table
        abbr_data = [["Abbreviation", "Full Name"]]
        abbr_data += [[abbr, full_name] for full_name, abbr in self.ABBREVIATIONS.items()]
        abbr_table = Table(abbr_data, colWidths=[100, 400])  # Only two columns
        abbr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(abbr_table)

        # Add spacing
        elements.append(Paragraph("<br/><br/>", styles['Normal']))

        # Detailed Results Table
        table_data = [["Code Smell", "File Path", "Line Number", "Effect"]]
        for item in self.current_report:
            code_smell = self.get_smell_abbreviation(item.get("code_smell", "Unknown"))
            file_path = Paragraph(item.get("file", "Unknown"), styles['Normal'])  # Wrap text
            line_number = str(item.get("line_number", "N/A"))
            effect = self.get_smell_effect(code_smell)
            table_data.append([code_smell, file_path, line_number, effect])

        # Adjust column widths for wrapping
        table = Table(table_data, colWidths=[100, 300, 80, 120])  # File Path column is wider
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)

        # Generate PDF
        doc.build(elements)
        messagebox.showinfo("Success", f"PDF report saved to {pdf_path}")


    def get_smell_effect(self, code_smell):
        """Return the effect/impact of a given code smell."""
        effects = {
            "LPL": "Maintainability",
            "LBCL": "Maintainability",
            "LC": "Maintainability",
            "LM": "Maintainability",
            "CCC": "Performance",
            "LLF": "Readability",
            "LTCE": "Readability",
            "LSC": "Maintainability",
            "LMC": "Performance",
        }
        return effects.get(code_smell, "Unknown")



def main():
    root = tk.Tk()
    app = CodeSmellDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()