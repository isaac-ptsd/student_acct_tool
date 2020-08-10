from __future__ import print_function
from gooey import Gooey, GooeyParser
import pandas as pd
import os.path


@Gooey(program_name="Account Setup Tool")
def main():
    """
    TODO:
        1) GUI with GOOEY
            * Parameters:
                * save location
                * CSV to read
                * Resulting file name
        2) Read a csv of student info exported from PS into a pandas DF (IN_DF)
        3) Create a new DF (OUT_DF) and populate with info from IN_DF
            * include logic to create additional AD required columns and values
    """
    parser = GooeyParser(description='some super cool title')
    parser.add_argument('output_directory',
                        action='store',
                        widget='DirChooser',
                        help="Output directory to save csv file")
    parser.add_argument('file_name',
                        action='store',
                        help="Save as:")
    parser.add_argument('ps_export',
                        action='store',
                        widget='FileChooser',
                        help="Select a PowerSchool export (.csv)")
    user_inputs = vars(parser.parse_args())

    output_dir = user_inputs['output_directory']
    file_name = user_inputs['file_name']
    ps_export_csv_in = user_inputs['ps_export']

    # NOTE the columns are: ['student_number', 'last_name', 'first_name', 'grade_level', 'school_id',
    #                        'web_id', 'web_password', 'student_web_id', 'student_web_password']
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
                                   'memberOf'])
    school_dict = {374: 'PHS', 373: 'TMS', 372: 'TES', 371: 'PES', 370: 'OES', 3247: 'ATI', 375: 'STEPS',
                   376: 'Transition', 1474: 'Crossroads'}
    # populate out_df
    for index, row in in_df.iterrows():
        school = school_dict[row['school_id']]
        ou_str = 'OU=' + school.lower() + ',OU=Students,DC=phoenix,DC=k12,DC=or,DC=us'
        first_last = row['first_name'] + '.' + row['last_name']
        if len(first_last) >= 18:
            first_last = row['first_name'][:1] + '.' + row['last_name']

        # 0 + grade_level + " " + last_name + ", " first_name
        out_df.at[index, 'cn'] = '0' + str(row['grade_level']) + row['last_name'] + row['first_name']
        # School ex: PHS
        out_df.at[index, 'department'] = school
        # ex: PHS Student
        out_df.at[index, 'description'] = school + ' Student'
        # === cn
        out_df.at[index, 'displayName'] = '0' + str(row['grade_level']) + ' ' + row['last_name'] + ', ' + row['first_name']
        # CN=010Aguirre\ ,Angel,OU=phs,OU=Students,DC=phoenix,DC=k12,DC=or,DC=us
        out_df.at[index, 'distinguishedName'] = 'CN=0' + str(row['grade_level']) + row['last_name'] + '\\ ,' \
                                                + row['first_name'] + ou_str
        # Angel
        out_df.at[index, 'givenName'] = row['first_name']
        # \\studentdata\phs-students\010Angel.Aguirre
        out_df.at[index, 'homeDirectory'] = '\\\\studentdata\\' + school.lower() + '-students\\0' \
                                            + str(row['grade_level']) + first_last
        # Angel.Aguirre@phoenixk12.org
        out_df.at[index, 'mail'] = row['first_name'] + '.' + row['last_name'] + '@phoenixk12.org'
        # 10Angel.Aguirre
        out_df.at[index, 'sAMAccountName'] = '0' + str(row['grade_level']) + row['first_name'] + '.' + row['last_name']
        # Aguirre
        out_df.at[index, 'sn'] = row['last_name']
        # Phs18648
        out_df.at[index, 'Password'] = school.lower().capitalize() + '' + str(row['student_number'])
        # 010Angel.Aguirre
        out_df.at[index, 'userPrincipalName'] = '0' + str(row['grade_level']) + first_last
        # always True
        out_df.at[index, 'CreateHomeDirectory'] = 'True'
        # student number
        out_df.at[index, 'id'] = row['student_number']
        # ex: 10
        out_df.at[index, 'grade'] = '0' + str(row['grade_level'])
        # OU=Phs,OU=Students,DC=phoenix,DC=k12,DC=or,DC=us
        out_df.at[index, 'destinationOU'] = 'OU=' + school.lower().capitalize() \
                                            + ',OU=Students,DC=phoenix,DC=k12,DC=or,DC=us'
        # CN=Phs-Student,OU=Students,DC=phoenix,DC=k12,DC=or,DC=12
        out_df.at[index, 'memberOf'] = 'CN=' + school.lower().capitalize() \
                                       + '-Student,OU=Students,DC=phoenix,DC=k12,DC=or,DC=12'

    out_df_by_school = out_df.groupby(['department', 'grade'])
    for group, data in out_df_by_school:
        output_file = os.path.join(output_dir, file_name + '_' + group[0] + '_' + group[1] + '.csv')
        data.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()