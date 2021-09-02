from __future__ import print_function
from gooey import Gooey, GooeyParser
import pandas as pd
import os.path

# global variables
last_name = ""
first_name = ""
first_last = ""


def isNaN(num):
    return num != num


@Gooey(program_name="Account Setup Tool")
def main():
    std_domain = '@phoenixk12.org'  # student domain

    parser = GooeyParser(description='PowerSchool export to Dovestone/Active Directory import file')
    parser.add_argument('Save Location',
                        action='store',
                        widget='DirChooser',
                        help="Output directory to save csv file")
    parser.add_argument('File Name',
                        action='store',
                        help="Save as:")
    parser.add_argument('PowerSchool Data Export',
                        action='store',
                        widget='FileChooser',
                        help="Select a PowerSchool export (.csv)")
    user_inputs = vars(parser.parse_args())
    output_dir = user_inputs['Save Location']
    file_name = user_inputs['File Name']
    ps_export_csv_in = user_inputs['PowerSchool Data Export']

    # NOTE: the in_df columns are: ['student_number', 'last_name', 'first_name', 'grade_level', 'school_id',
    #                               'web_id', 'web_password', 'student_web_id', 'student_web_password',
    #                               'student_email', 'student_web_id']
    in_df = pd.read_csv(ps_export_csv_in, encoding='latin1')
    in_df.columns = map(str.lower, in_df.columns)  # column names to lowercase
    out_df = pd.DataFrame(columns=['cn',
                                   'department',
                                   'description',
                                   'displayName',
                                   'distinguishedName',
                                   'givenName',
                                   'homeDirectory',
                                   'mail',
                                   'sAMAccountName',
                                   'sn',
                                   'Password',
                                   'userPrincipalName',
                                   'CreateHomeDirectory',
                                   'id',
                                   'grade',
                                   'destinationOU',
                                   'memberOf',
                                   'PasswordNeverExpires',
                                   'UserCannotChangePassword',
                                   'Office'])
    # Data frame to create CSV for resetting passwords
    out_df_pw = pd.DataFrame(columns=['memberOf', 'sAMAccountName', 'password', 'Modify'])

    school_dict = {374: 'PHS', 373: 'TMS', 372: 'TES', 371: 'PES', 370: 'OES', 3247: 'ATI', 375: 'STEPS',
                   376: 'Transition', 1474: 'Crossroads', 377: 'PTR', 79438: 'ENR'}
    # populate out_df
    bad_chars = [';', ':', '!', "*", '\'', '\"', '`']
    for index, row in in_df.iterrows():
        global last_name
        global first_name
        global first_last

        school = school_dict[row['school_id']]
        ou_str = 'OU=' + school.lower() + ',OU=Students,DC=phoenix,DC=k12,DC=or,DC=us'

        if len(str(row['grade_level'])) >= 2:
            grade_level = str(row['grade_level'])
        else:
            grade_level = '0' + str(row['grade_level'])

        #  NAME LOGIC
        # TODO: check for student_web_id, if present, use for last_name, first_name and first_last

        if isNaN(row['student_web_id']) or row['student_web_id'].find('.') == -1:
            last_name = row['last_name'].replace('-', ' ').lower().split()
            if len(last_name) >= 2:
                if last_name[0] == 'de' and last_name[1] == 'la':
                    last_name = last_name[0].capitalize() + last_name[1].capitalize() + last_name[2].capitalize()
                elif (last_name[0] == 'de' and last_name[1] != 'la') or (last_name[0] == 'ah') or (last_name[0] == 'van'):
                    last_name = last_name[0].capitalize() + last_name[1].capitalize()
                else:
                    last_name = last_name[0].capitalize()
            else:
                last_name = last_name[0].capitalize()
            last_name = ''.join(i for i in last_name if i not in bad_chars)

            first_name = row['first_name']
            first_name = ''.join(i for i in first_name if i not in bad_chars)

        else:
            name_split = row['student_web_id'].split('.')
            first_name = name_split[0][2:]  # strips the grade level off the first name (01john -> john)
            last_name = name_split[1]

        first_last = first_name + '.' + last_name
        if len(first_last) >= 18:
            first_last = first_name[:1] + '.' + last_name

        #  END NAME LOGIC

        student_email = row['student_email']
        if isNaN(student_email) or std_domain not in student_email:
            student_email = first_last + std_domain

        # 0 + grade_level + " " + last_name + ", " first_name
        out_df.at[index, 'cn'] = grade_level + ' ' + last_name + ', ' + first_name
        # School ex: PHS
        out_df.at[index, 'department'] = school
        # ex: PHS Student
        out_df.at[index, 'description'] = school + ' Student'
        # === cn
        out_df.at[index, 'displayName'] = grade_level + ' ' + last_name + ', ' + \
            first_name
        # CN=010LastName\ ,FirstName,OU=phs,OU=Students,DC=phoenix,DC=k12,DC=or,DC=us
        out_df.at[index, 'distinguishedName'] = 'CN=' + grade_level + last_name + '\\ ,' + first_name + ', ' + ou_str
        # FirstName
        out_df.at[index, 'givenName'] = first_name
        # \\studentdata\phs-students\010FirstName.LastName
        out_df.at[index, 'homeDirectory'] = '\\\\studentdata\\' + school.lower() + '-students\\' +\
                                            grade_level + first_last
        # FirstName.LastName@phoenixk12.org
        out_df.at[index, 'mail'] = student_email
        # FirstName.LastName
        out_df.at[index, 'sAMAccountName'] = grade_level + first_last
        # LastName
        out_df.at[index, 'sn'] = last_name
        # Phs18648
        out_df.at[index, 'Password'] = school.lower().capitalize() + '' + str(row['student_number'])
        # 010FirstName.LastName
        out_df.at[index, 'userPrincipalName'] = grade_level + first_last + std_domain
        # always True
        out_df.at[index, 'CreateHomeDirectory'] = 'True'
        # student number
        out_df.at[index, 'id'] = row['student_number']
        # ex: 10
        out_df.at[index, 'grade'] = grade_level
        # OU=Phs,OU=Students,DC=phoenix,DC=k12,DC=or,DC=us
        out_df.at[index, 'destinationOU'] = 'OU=' + school.lower().capitalize() \
                                            + ',OU=Students,DC=phoenix,DC=k12,DC=or,DC=us'
        # CN=Phs-Student,OU=Students,DC=phoenix,DC=k12,DC=or,DC=12
        out_df.at[index, 'memberOf'] = 'CN=' + school.lower().capitalize() \
                                       + '-Student,OU=Students,DC=phoenix,DC=k12,DC=or,DC=12'
        # always True
        out_df.at[index, 'PasswordNeverExpires'] = 'True'
        # always True
        out_df.at[index, 'UserCannotChangePassword'] = 'True'
        out_df.at[index, 'Office'] = school

        # create CSV to reset passwords
        out_df_pw.at[index, 'memberOf'] = 'CN=' + school.lower().capitalize() \
                                          + '-Student,OU=Students,DC=phoenix,DC=k12,DC=or,DC=12'
        out_df_pw.at[index, 'sAMAccountName'] = grade_level + first_last
        out_df_pw.at[index, 'password'] = school.lower().capitalize() + '' + str(row['student_number'])
        out_df_pw.at[index, 'Modify'] = True

    ####################################################################################################################
    # We don't seem to need this with the latest version of google sync:
    # out_df_pw_by_school = out_df_pw.groupby(out_df_pw.password.str[:3])
    # for pw_group, pw_data in out_df_pw_by_school:
    #     pw_output_file = os.path.join(output_dir, file_name + '_' + pw_group + '_password_reset.csv')
    #     pw_data.to_csv(pw_output_file, index=False)
    ####################################################################################################################

    out_df_by_school = out_df.groupby(['department', 'grade'])
    for group, data in out_df_by_school:
        output_file = os.path.join(output_dir, file_name + '_' + group[0] + '_' + group[1] + '.csv')
        data.to_csv(output_file, index=False)

    master_output_file = os.path.join(output_dir, 'MASTER_' + file_name + '.csv')
    out_df.to_csv(master_output_file, index=False)

    account_output_file = os.path.join(output_dir, 'SIS_account_import_' + file_name + '.csv')
    account_file_df = out_df[['id', 'sAMAccountName', 'Password']].copy()
    account_file_df.to_csv(account_output_file, index=False)

    email_output_file = os.path.join(output_dir, 'SIS_email_import_' + file_name + '.csv')
    email_file_df = out_df[['id', 'mail']].copy()
    email_file_df.to_csv(email_output_file, index=False)


if __name__ == '__main__':
    main()
