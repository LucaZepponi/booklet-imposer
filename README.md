
# 📗 Booklet-Imposer

Booklet-Imposer is a class in python that organises and divides a PDF file, given as input, into an appropriate number of booklet-ready files.
The graphical interface was developed in Python using Tkinter and is designed to avoid tedious manual operations.



## ✨ Features

- Intuitive graphical interface: GUI made with Tkinter creates a simple graphical window accessible even to non-expert users
- PDF file selection from interface: it allows the selection of the PDF file to be processed via the file system dialogue
- Output organised in separate bundles: it automatically splits the original PDF document into separate bundles to facilitate the collection of sheets in the same bundle
- Automatic blank page handling: it automatically adds the right number of blank pages to manage correct booklet layouts
- Setup for double-sided printing: it rearranges pages according to a double-sided printing scheme, ready to be folded and bound
- Customisable prefix for generated PDF files: each exported file has a customisable name with a progressive sequential number
- Automatic generation of information files (`.txt`): it associates the set of output PDF files with a `.txt` file containing some useful metadata
- Robust error handling: it checks for invalid inputs, missing files or password-protected PDFs, with clear error messages



## 💻 Requirements

- Python 3.8 or higher
- Python modules:
  - `tkinter`
  - `PyPDF2`
  - `pathlib`
  - `ttk` (incluso in `tkinter`)

You can install the necessary packages with

```bash
pip install -r requirements.txt
```

## 🛠️ Installation

1. Clone the repository to your local machine:

    ```bash
        git clone https://github.com/LucaZepponi/booklet-imposer.git
        cd Booklet-Imposer
    ```
2. run the application
    ```bash
        python main.py
    ```



## 💡 Usage
💻 Running the application
1. Make sure you have Python ≥ 3.8 installed on your system
2. Install the required dependencies (see section 🛠️ Installation)
3. Start the programme:
```bash
python main.py
```

🧩 Passaggi nell'interfaccia
1. Select the original PDF: click on `Sfoglia` next to `Input PDF` and choose the file to be split into files
2. Choose output folder: click on `Sfoglia` next to `Cartella di output` and choose where to save the files to be generated
3. Set the number of sheets per file: enter the desired number
4. Prefix the output files: for example, with `file`, files such as `file_1.pdf`, `file_2.pdf`, etc. will be generated.
5. Click on `Crea fascicoli`: the programme will process the PDF file and show the progress via a progress bar



## 📁 File Structure

```
Booklet-Imposer
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```


## 📜 License

[GNU AFFERO GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/agpl-3.0.en.html#license-text)



## 👨🏻‍💻 Authors

- [Luca Zepponi](https://github.com/LucaZepponi)
