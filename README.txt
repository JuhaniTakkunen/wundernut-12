This is a solution to a Wundernut-12.
https://github.com/wunderdogsw/wundernut-vol12


Requirements:
    - Python 3.10 (64-bit)  - might work with other versions as well
    - Tesseract 5  - might work with other versions as well
        * Tesseract must be found in the PATH,
        * OR it can be added into TESSERACT_EXE -variable in main.py


How to run the code:
Step 1: install requirements
>> python -m pip install -r requirements.txt

Step 2: run the code
>> python main.py

Output/result WITH SPACES will be in the console.

Common errors:
    - pytesseract.pytesseract.TesseractNotFoundError:
        * Check that Tesseract is installed and added to path
    - FileNotFoundError: [Errno 2] No such file or directory: 'parchment.png'
        * ensure that your working directory is the same where main.py file is located in