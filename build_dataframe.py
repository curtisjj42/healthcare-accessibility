import pandas as pd
import re


def normalize_string(s):
    return re.sub(r'[^\w\s]', '', s).lower()


def build_dataframe(sites_df):
    hospital_df = sites_df['Hospital Information']
    hospital_df['Facility type'] = 'Hospital'
    hospital_df.rename(columns={'Short name': 'Facility name'}, inplace=True)

    snf_df = sites_df['Nursing home information']
    dist_df = sites_df['Nursing homes within 30 minutes']

    hospital_df['norm_address'] = hospital_df['Address'].apply(normalize_string)
    hospital_df['norm_name'] = hospital_df['Facility name'].apply(normalize_string)
    hospital_df['norm_full_name'] = hospital_df['Hospital'].apply(normalize_string)

    snf_df['norm_address'] = snf_df['Address'].apply(normalize_string)
    snf_df['norm_name'] = snf_df['Facility name'].apply(normalize_string)

    dist_df['norm_hosp'] = dist_df['Hospital'].apply(normalize_string)
    dist_df['norm_snf'] = dist_df['Nursing homes within 30 minutes drive time'].apply(normalize_string)

    snf_30_count = dist_df[['norm_hosp', 'Nursing homes within 30 minutes drive time']].groupby(['norm_hosp']).count()
    hosp_30_count = dist_df[['norm_snf', 'norm_hosp']].groupby(['norm_snf']).count()
    hosp_30_count.rename(columns={'norm_hosp': 'Hospitals within 30 minutes drive time'}, inplace=True)

    mass_df = pd.merge(hospital_df, snf_30_count, how='left', left_on='norm_full_name', right_on='norm_hosp')

    facility_info = pd.concat([mass_df, snf_df], ignore_index=True)
    facility_info = pd.merge(facility_info, hosp_30_count, how='left', left_on='norm_name', right_on='norm_snf')

    facility_info['Hospitals within 30 minutes drive time'] = facility_info[
        'Hospitals within 30 minutes drive time'].combine_first(
        facility_info['Number of hospitals within 30 minute drive time'])
    facility_info['norm_name'] = facility_info['norm_full_name'].combine_first(facility_info['norm_name'])

    facility_info.drop(columns=['Number of hospitals within 30 minute drive time', 'norm_full_name'], inplace=True)

    return facility_info


def main():

    sites_df = pd.read_excel('health-care-capacity-dashboard-10-16-2024_updated.xlsx', sheet_name=None)

    facility_info = build_dataframe(sites_df)
    facility_info.to_csv('Inpatient Healthcare Facilities in Massachusetts.csv', index=False)


if __name__ == '__main__':
    main()