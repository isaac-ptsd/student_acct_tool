# student_acct_tool

will be used to automate the initial setup required for student account creation. 

This program will read in a csv file generated out of PowerSchool, and prepare it for use with the DoveStone Active Directory softwear. 

To build the executable: 
`pyinstaller --noconsole --hidden-import=pkg_resources.py2_warn --onefile account_setup_tool.py`