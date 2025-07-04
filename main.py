from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter.simpledialog import askstring

# PyPDF manages the file's reader and writing
# Pathlib improves the path's management compared to strings
# tkinter (and associated modules) biulds the GUI
# asktring is usefull to insert the password for PDF decryption

class BookletImposer:
  # BookletImposer class' constructor
  def __init__(self,
               input_path: str,
               output_folder: str,
               fogli_per_blocco: int = 5,
               prefix: str = "fascicolo"):
    """`BookletImposer` class' constructor.

    Args:
      input_path (str): .pdf file path.
      output_folder (str): Output's folder path.
      fogli_per_blocco (int, optional): Number of sheets to be used to complete a file. Defaults to 5.
      prefix (str, optional): Name to be used to save the various files. Defaults to 'file'.

    Raises:
      RuntimeError: If the user cancels entering the password for a protected PDF.
    """
    # Class attributes
    self.input_path = Path(input_path)       # Path of the .pdf file to be reorganised
    self.output_folder = Path(output_folder) # Folder where files are saved
    self.fogli_per_blocco = fogli_per_blocco # Number of sheets of which each block is composed
    self.reader = PdfReader(self.input_path) # .pdf file loaded by the user
    
    # If the PDF is password protected, ask the user with a popup
    if self.reader.is_encrypted:
      while True:
        pwd = askstring("Password richiesta", "Il PDF è protetto da password. Inserici la password:", show="*")
        if pwd is None: # The user pressed "Cancel"
          raise RuntimeError("Operazione annullata dall'utente.")
        # self.reader.decrypt(pwd) returns an int: 0 or 1
        if self.reader.decrypt(pwd) != 0:
          break # Correct password: exit from while
        else:
          messagebox.showerror("Errore", "Password sbagliata, riprova")
    
    # They must be placed after decrypting the PDF, otherwise the programme crashes
    self.total_pages_original = len(self.reader.pages) # Number of pages of the original .pdf file
    self.pagine_per_blocco = self.fogli_per_blocco * 4 # Number of pages per file
    # Each sheet corresponds to 4 double-sided printable pages (2 per side)
    self.prefix = prefix # Useful prefix to save the various files
    self.all_pages_with_blanks = [] # List of all pages in the PDF with also blank pages # TODO : Probabilmente può essere eliminato. Posso sovrascrivere tutto in total_pages_original
    self.total_pages_with_blanks = len(self.all_pages_with_blanks) # Total number of pages after adding blank pages
    
  def add_blank_pages(self) -> list:
    """It adds as many `None` pages as necessary so that the last booklet consists of the same number of pages as the others.

    Returns:
      pages (list): New list of pages in the PDF with an appropriate number of blank pages added at the bottom to complete the file.
    """
    # Transforms the pages of the original PDF into a list
    # pages = list(self.reader.pages) is not good, because I need to access the currently saved pages, so the version with the `None` pages
    pages = list(self.all_pages_with_blanks)
    # Extracts the number of pages of the original PDF
    total_original_pages = len(pages)
    # Calculate how many blank pages are to be added
    remainder = total_original_pages % self.pagine_per_blocco
    # If there are pages to be added, ...
    if remainder != 0:
      # ... he adds
      for _ in range(self.pagine_per_blocco - remainder):
        pages.append(None)
    return pages
  
  
  
  def imposition_order(self, pages: list) -> list:
    """Sort the printers according to typographic logic for folding prints (last and first, penultimate and second, etc.).
    Alternate left and right pages according to the actual print layout.
    
    The file consists of quatrains of pages: each sheet contains four pages. In particular:
    - on the facing page there is page `A` on the left and page `B` on the right,
    - while on the back page there are page `C` to the left and page `D` to the right.

    Args:
      pages (list[PageObject]): Page range of the original PDF to be included in the same file.

    Returns:
      imposed (list): Pages from the original PDF rearranged in the appropriate order
    """
    # Initialise imposed
    imposed = []           # `imposed` will contain the final order of the pages in the file
    
    left = 0               # `left` starts at the top of the list of pages in the PDF
    right = len(pages) - 1 # right` starts at the end
    
    for _ in range(len(pages) // 4): # Each cycle handles 4 pages (i.e. one sheet)
      imposed.append(pages[right])   # Front left -> outer left page
      imposed.append(pages[left])    # Fronte destro -> pagina esterna destra
      
      left += 1
      right -= 1
      
      imposed.append(pages[left])  # Back left -> inside left page
      imposed.append(pages[right]) # Retro destro -> internal page right
      
      # I prepare the indices for the next sheet
      left += 1
      right -= 1
    return imposed
  
  
  
  def process_block(self, i: int) -> None:
    """Creates a file by rearranging the pages of the original PDF for booklet printing.

    For the `i`-th block:
    - Selects the corresponding pages.
    - Rearranges the pages in the order of imposition.
    - Generates a new PDF file ready for double-sided printing.
    - Also saves a .txt file with general information about the document.

    Args:
      i (int): Index of the phablet to be generated (0-based).
    """
    # Page range calculation: determines the page range of which the block `i` is composed.
    start = i * self.pagine_per_blocco
    end = start + self.pagine_per_blocco
    
    # Extracts pages by building a kind of `PyPDF2` list
    temp_pages = self.all_pages_with_blanks[start:end]
    
    # Rearranging the pages according to the logic of booklet printing
    ordered_pages = self.imposition_order(temp_pages)
    
    # Turns `None` pages into blank pages
    writer = PdfWriter()
    for page in ordered_pages:
      if page is None:
        width = self.reader.pages[0].mediabox.width
        height = self.reader.pages[0].mediabox.height
        writer.add_blank_page(width=width, height=height)
      else:
        writer.add_page(page)
        
    # Save files
    name = f"{self.prefix}_{i+1}"
    output_pdf_path = self.output_folder / f"{name}.pdf"
    with open(output_pdf_path, "wb") as f:
      writer.write(f)
    
    # Save the information file type .txt
    self.create_info_file()
  
  
  
  def create_info_file(self) -> None:
    """Create the information document with the main information you need to know for proper binding.
    
    The .txt document contains:
    - The name of the analysed PDF file.
    - The total number of pages of the original PDF
    - The estimated number of sheets it will take to print all the files
    - The size of the pages.
    - The thickness of the spine.
    """
    # .txt file's path
    output_txt_path = self.output_folder / f"{self.prefix}_info.txt" 
    # I extract the dimensions of the first and last page (all pages are the same size)
    first = self.reader.pages[0].mediabox
    pt_to_mm = 0.3528 # Height and width will be expressed in pt (typographic points): conversion factor pt -> mm
    width_first = float(first.width) * pt_to_mm
    height_first = float(first.height) * pt_to_mm
    
    # Number of A4 sheets the printer will use to print the booklet
    num_blocks = (self.total_pages_original + self.pagine_per_blocco - 1) // self.pagine_per_blocco # Round up
    num_paper_to_use = num_blocks * self.fogli_per_blocco
    
    # Back thickness calculation
    PAPER_THICKNESS = 0.1 # millimeters
    # TODO : Mettere un entry per questo dato : la grammatura del foglio può essere diversa
    thickness_back = num_paper_to_use * PAPER_THICKNESS
    
    # Write .txt files
    with open(output_txt_path, mode="w", encoding="utf-8") as txt:
      txt.write(f"File analizzato: {self. input_path.name}\n")
      txt.write(f"Totale pagine: {self.total_pages_original}\n")
      txt.write(f"Totale fogli stimati: {num_paper_to_use}\n")
      txt.write(f"Dimensioni pagine: {width_first:.2f} x {height_first:.2f} mm\n")
      txt.write(f"Spessore dorso: {thickness_back:.2f} mm\n")
      
    
    
  @staticmethod
  def PDF_selection(entry_widget: Entry) -> None:
    """It creates the system window to choose the PDF without writing the entire file path by hand.

    Args:
      entry_widget (Entry): Entry field in which to enter the path to the selected file.
    """
    # File selection window
    filename = filedialog.askopenfilename( # Create the system window
      title="Seleziona il file PDF.",
      filetypes=[("PDF files", "*.pdf")],  # Restrict selection to .pdf files only
      defaultextension=".pdf"              # Useful if you manually enter the file name without an extension
    )
    
    # Writing in the input field
    if filename: # Ensures that the user has not cancelled the input window
      entry_widget.delete(0, END)      # Delete existing text in the field
      entry_widget.insert(0, filename) # Writes the path to the selected file
    
  @staticmethod
  def folder_selection(entry_widget: Entry):
    """It creates the system window to choose the folder where the PDF is to be saved without writing the entire folder path by hand.

    Args:
      entry_widget (Entry): Entry field where you enter the path to the folder where the PDF file is to be saved.
    """
    folder = filedialog.askdirectory(title="Seleziona cartella di output.") # Open the system dialogue box for selecting a directory
    if folder:                       # Check Selection
      entry_widget.delete(0, END)    # Delete current content
      entry_widget.insert(0, folder) # Inserts the selected route
  
  @staticmethod
  def start_gui() -> None:
    """Launches the graphical interface for the creation of booklet print files.
    
    The GUI allows the user to:
    - select an input PDF file,
    - choose the output folder,
    - set the number of pages per block,
    - define a prefix for the generated files,
    - start the file generation process,
    close the application,
    - monitor progress via a progress bar.
    
    Use Tkinter for window construction and event management.
    """
    def start_elaboration() -> None:
      """Starts the file creation process from the data entered in the GUI.

      It extracts data from the input fields (PDF file, output folder, number of pages per booklet, prefix), validates user-supplied input, and in cases of correctness proceeds with booklet generation via the `BookletImposer` class.

      It adds the appropriate number of `None` pages to ensure that all files that will be created have the same size.
      
      During processing, it updates the progressbar to provide visual feedback, handles any errors by displaying dialog boxes, and sets the cursor to 'wait' to indicate to the user that the operation is in progress.

      If an error occurs (invalid input, non-existent file, exceptions during processing), an error message is displayed and the process is aborted without stopping the GUI.

      At the end of the process, it restores the cursor to normal mode.

      It receives no updates and returns no values.
      """
      # Extraction of user-entered data in the GUI
      input_pdf = entry_input_PDF.get()
      output_folder = entry_output_PDF.get()
      
      # Conversion and validation of the number of pages per block
      try:
        pages = int(entry_number_pages_per_block.get()) # Try converting
      except ValueError:
        # If the conversion fails (non-numeric input), it displays an error message
        messagebox.showerror("Errore", "⚠️ Inserire un numero valido di fogli.")
        return
      
      prefix = entry_prefix.get() # Prefix for output file names
      
      # Validation of the input PDF file
      if not input_pdf.lower().endswith(".pdf") or not Path(input_pdf).exists():
        messagebox.showerror("Errore", "⚠️ Il file selezionato non è un PDF valido.")
        return # return in case of error to not continue
      
      # Output folder validation
      if not output_folder or not Path(output_folder).exists():
        messagebox.showerror("Errore", "⚠️ Seleziona una cartella di output esistente.")
        return
      
      # Sets the cursor to 'wait' mode to indicate that the programme is working
      root.config(cursor="wait")
      root.update()
        
      try:
        # Creation of the BookletImposer instance with user-supplied parameters
        imposer = BookletImposer(input_pdf, output_folder, pages, prefix)
        
        # Overwrites the pages of the imposer with the new list
        pagine_modificate = list(imposer.reader.pages)
        
        # I will now add two start pages and two more end pages in order to insert a hardcover
        pagine_modificate = [None, None] + pagine_modificate + [None, None]
        
        # I update the pages in the imposer
        imposer.all_pages_with_blanks = pagine_modificate
        imposer.total_pages_with_blanks = len(imposer.all_pages_with_blanks)
        
        # Adding additional blank pages to close the last file
        imposer.all_pages_with_blanks = imposer.add_blank_pages()
        imposer.total_pages_with_blanks = len(imposer.all_pages_with_blanks)

        # Calculate the total number of files to be created
        total_blocks = (imposer.total_pages_with_blanks + imposer.pagine_per_blocco - 1) // imposer.pagine_per_blocco
        
        # Configure the progress bar with the maximum number of blocks
        progress["maximum"] = total_blocks
        # and initialise progress to 0
        progress["value"] = 0
        
        # Cycle to process each block and update the progress bar
        for i in range(total_blocks):
          imposer.process_block(i)
          progress["value"] += 1
          root.update() # Update GUI to reflect visual changes
        
        # Message at the end of the creation of all files
        messagebox.showinfo("Fascicoli creati.", "✅ I fascicoli sono stati creati con successo.")
      except RuntimeError as e:
        # Here I catch the exception raised if the password is wrong or cancelled
        messagebox.showerror("Errore", str(e))
        return
      except Exception as e:
        # Handling of other exceptions that may occur during processing
        messagebox.showerror("Errore", f"Errore {e}.")
      
      # Resets the cursor to 'normal' mode even in the event of an error
      root.config(cursor="")
      root.update()
    
    
      
    # Initialising the main window
    root = Tk()
    root.title("Crea fascicoli per libretto") # Title
    root.geometry("400x250")                  # Size
    
    # I set the column weight to tell Tkinter that column 1 can grow
    root.columnconfigure(1, weight=1)
    
    label_width = 100 # Length used for Entry fields
    
    # Label and input field to select the PDF to be edited
    Label(root, text="Input PDF:").grid(row=0, column=0, sticky=W)
    entry_input_PDF = Entry(root, width=label_width)
    entry_input_PDF.grid(row=0, column=1, sticky="ew")
    
    # Horizontal Scrollbar for Input PDF Entry
    scrollbar_input = Scrollbar(root, orient=HORIZONTAL, command=entry_input_PDF.xview)
    scrollbar_input.grid(row=1, column=1, sticky="ew")
    
    # Bidirectional link between entry and Scrollbar
    entry_input_PDF.config(xscrollcommand=scrollbar_input.set)
    
    # Browse' button that opens the file dialogue to select a PDF
    Button(root, text="Sfoglia", command=lambda: BookletImposer.PDF_selection(entry_input_PDF)).grid(row=0, column=2, padx=5)
    
    # Selection of the folder where to save the blocks
    Label(root, text="Cartella di output:").grid(row=2, column=0, sticky=W)
    entry_output_PDF = Entry(root, width=label_width)
    entry_output_PDF.grid(row=2, column=1, pady=2, sticky="ew")
    # Scrollbar for Output Folder Entry
    scrollbar_output = Scrollbar(root, orient=HORIZONTAL, command=entry_output_PDF.xview)
    scrollbar_output.grid(row=3, column=1, sticky="ew")
    # Bi-directional connection between Entry and Scrollbar
    entry_output_PDF.config(xscrollcommand=scrollbar_output.set)
    # Browse' button that opens the dialogue to select the output folder
    Button(root, text="Sfoglia", command=lambda: BookletImposer.folder_selection(entry_output_PDF)).grid(row=2, column=2, padx=5)
    
    # Label and input field for the number of sheets per booklet
    Label(root, text="Fogli per libretto:").grid(row=4, column=0, sticky=W)
    entry_number_pages_per_block = Entry(root, width=label_width)
    entry_number_pages_per_block.grid(row=4, column=1, pady=2, sticky="ew")

    # Label and input field for prefixing output files
    Label(root, text="Prefisso nome file:").grid(row=5, column=0, sticky=W)
    entry_prefix = Entry(root, width=label_width)
    entry_prefix.insert(0, "fascicolo")
    entry_prefix.grid(row=5, column=1, pady=2, sticky="ew")
    
    # Button to start the file creation
    Button(root, text="Crea Fascicoli", command=lambda: start_elaboration()).grid(row=6, column=1, pady=5)
    
    # Button for closing the GUI
    Button(root, text="Chiudi", command=lambda: root.destroy()).grid(row=7, column=1, pady=5)
    
    # Progress bar to display processing progress
    progress = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
    progress.grid(row=8, column=0, columnspan=3, pady=10)
    
    # Starting the main GUI cycle (event loop)
    root.mainloop()
    
# Script entry point: starts the GUI if the file is executed as main program
if __name__ == "__main__":
  BookletImposer.start_gui()