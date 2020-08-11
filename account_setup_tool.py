from __future__ import print_function
from gooey import Gooey, GooeyParser
import pandas as pd
import os.path


@Gooey(program_name="Account Setup Tool")
def main():
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
    #                               'web_id', 'web_password', 'student_web_id', 'student_web_password']
    in_df = pd.read_csv(ps_export_csv_in)
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
                                   'UserCannotChangePassword'])
    school_dict = {374: 'PHS', 373: 'TMS', 372: 'TES', 371: 'PES', 370: 'OES', 3247: 'ATI', 375: 'STEPS',
                   376: 'Transition', 1474: 'Crossroads'}
    # populate out_df
    for index, row in in_df.iterrows():
        school = school_dict[row['school_id']]
        ou_str = 'OU=' + school.lower() + ',OU=Students,DC=phoenix,DC=k12,DC=or,DC=us'
        if len(str(row['grade_level'])) >= 2:
            grade_level = str(row['grade_level'])
        else:
            grade_level = '0' + str(row['grade_level'])
        first_last = row['first_name'] + '.' + row['last_name'].split()[0]
        if len(first_last) >= 18:
            first_last = row['first_name'][:1] + '.' + row['last_name'].split()[0]

        # 0 + grade_level + " " + last_name + ", " first_name
        out_df.at[index, 'cn'] = grade_level + ' ' + row['last_name'].split()[0] + ', ' + row['first_name']
        # School ex: PHS
        out_df.at[index, 'department'] = school
        # ex: PHS Student
        out_df.at[index, 'description'] = school + ' Student'
        # === cn
        out_df.at[index, 'displayName'] = grade_level + ' ' + row['last_name'].split()[0] + ', ' + row['first_name']
        # CN=010Aguirre\ ,Angel,OU=phs,OU=Students,DC=phoenix,DC=k12,DC=or,DC=us
        out_df.at[index, 'distinguishedName'] = 'CN=0' + grade_level + row['last_name'].split()[0] \
                                                + '\\ ,' + row['first_name'] + ', ' + ou_str
        # Angel
        out_df.at[index, 'givenName'] = row['first_name']
        # \\studentdata\phs-students\010Angel.Aguirre
        out_df.at[index, 'homeDirectory'] = '\\\\studentdata\\' + school.lower() + '-students\\' \
                                            + grade_level + first_last
        # Angel.Aguirre@phoenixk12.org
        out_df.at[index, 'mail'] = first_last + '@phoenixk12.org'
        # 10Angel.Aguirre
        out_df.at[index, 'sAMAccountName'] = grade_level + first_last
        # Aguirre
        out_df.at[index, 'sn'] = row['last_name'].split()[0]
        # Phs18648
        out_df.at[index, 'Password'] = school.lower().capitalize() + '' + str(row['student_number'])
        # 010Angel.Aguirre
        out_df.at[index, 'userPrincipalName'] = grade_level + first_last
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

    out_df_by_school = out_df.groupby(['department', 'grade'])
    for group, data in out_df_by_school:
        output_file = os.path.join(output_dir, file_name + '_' + group[0] + '_' + group[1] + '.csv')
        data.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()
