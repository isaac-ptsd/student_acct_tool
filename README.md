# student_acct_tool

will be used to automate the initial setup required for student account creation. 

This program will read in a csv file generated out of PowerSchool, 
and prepare it for use with the DoveStone Active Directory software. 

To build the executable: 
`pyinstaller --noconsole --hidden-import=pkg_resources.py2_warn --onefile account_setup_tool.py`


SQL to perform direct export from DB:
```
SELECT
    students.student_number as student_number,
    students.last_name as last_name,
    students.first_name as first_name,
    students.grade_level as grade_level,
    students.schoolid as school_id,
    emailaddress.emailaddress as student**_email
FROM 
    students
    LEFT OUTER JOIN
        person
        ON 
            students.person_id = person.id
    LEFT OUTER JOIN 
        personemailaddressassoc
        ON 
            person.id = personemailaddressassoc.personid
    LEFT OUTER JOIN 
        emailaddress
        ON
            personemailaddressassoc.emailaddressid = emailaddress.emailaddressid
WHERE 
    enroll_status = -1 
    OR
    enroll_status = 0;
```

NOTE: Some students will not have an email entered saved in PS SIS.
We need to verify against the Google account management system.

