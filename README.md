# student_acct_tool

will be used to automate the initial setup required for student account creation. 

This program will read in a csv file generated out of PowerSchool, 
and prepare it for use with the Dovestones Software AD Bulk Users. 

To build the executable: 
`pyinstaller --noconsole --hidden-import=pkg_resources.py2_warn --onefile account_setup_tool.py`


SQL to perform direct export from DB:
```
SELECT
    students.student_number as student_number,
    students.last_name as last_name,
    students.first_name as first_name,
    students.grade_level as grade_level,
    students.student_web_id,
    CASE 
        -- I use the U_ECOLLECT_ENROLL.SCHOOLID field for students at the enrollment school
        -- this will ensure that new students will have their accounts setup for the school
        -- they will be attending and NOT the enrollment school
        students.schoolid when 79438 then to_number(U_ECOLLECT_ENROLL.SCHOOLID)
        ELSE 
        students.schoolid 
    END as school_id,
    emailaddress.emailaddress as student_email
FROM 
    students
    LEFT OUTER JOIN
    U_ECOLLECT_ENROLL 
    ON
        u_ecollect_enroll.studentsdcid = students.dcid
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

