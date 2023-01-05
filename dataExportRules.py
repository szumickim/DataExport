import time
import numpy as np
import pandas as pd
import collections as co
import os
import datetime as dt

# files
EXPORT_FOLDER_NAME: str = r'C:\Users\plocitom\PycharmProjects\dataExport\exports'
DATA_EXPORT_FILE_NAME: str = '2022-12-28_data_export.csv'
GSH_FILE_NAME: str = 'Group Supplier handling 21-12-2022.xlsx'
LEGEND_FILE_NAME: str = 'legenda.xlsx'

# Sheet names
ITEM_CATEGORY_SHEET_NAME: str = 'Item Category'
GLOBAL_HIERARCHY_SHEET_NAME: str = 'GH'
NECESSARY_MAPPING_SHEET_NAME: str = 'Necessary Mapping'
GSH_SHEET_NAME: str = 'GSH'


# random const
LIST_OF_VENDOR_PHRASE: str = 'list of vendor'
NON_ACTIVE_STATUS: str = 'Non-active'

# Headers
ITEM_CATEGORY_HEADER: str = 'ITEMCATGROUP'
GLOBAL_HIERARCHY_HEADER: str = 'Product Line'
MATERIAL_GROUP_HEADER: str = 'MAT_GROUP'
GH_MC0_HEADER: str = 'NEW ID MC0, GH 2020'
GH_PRODUCT_LINE_HEADER: str = 'Product line whole sale EN'
NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER: str = 'NECESSARY_FILL'
FEATURES_LIST_HEADER: str = 'FEATURES_COUNT'
MAX_NECESSARY_FEATURES_LIST_HEADER: str = 'MAX_NECESSARY_FEATURES_LIST'

DATA_EXPORT_VENDOR_TYPE_HEADER: str = 'Vendor Local/Multi'
GSH_VENDOR_TYPE_HEADER: str = 'Multi-/local'
GSH_VENDOR_HEADER: str = 'Vendor'
GROUP_SUPPLIER_NAME_HEADER: str = 'GROUP_SUPPLIER_NAME'
PIM_PERSON_RESPONSIBLE_HEADER: str = 'Person Responsible'
SALES_STATUS_HEADER: str = 'SALESSTATUS'
SALES_ORG_HEADER: str = 'SALESORG'


def read_all_cache_data_exports() -> pd.DataFrame:
    # list the files
    filelist = os.listdir(EXPORT_FOLDER_NAME)

    # read them into pandas
    df_list = [pd.read_csv(EXPORT_FOLDER_NAME + '\\' + file, sep=',', dtype='string', keep_default_na=False)
               for file in filelist]

    # join them together
    return pd.concat(df_list)




def read_cache_data_export() -> pd.DataFrame:
    df = pd.read_csv(DATA_EXPORT_FILE_NAME, sep=',', dtype='string')
    return df.fillna('')


def apply_item_category_dictionary(df_data_export: pd.DataFrame) -> pd.DataFrame:
    # Mapping of the STEP Item Category names from legenda.xlsx e.g. BANC --> Cross Dock
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=ITEM_CATEGORY_SHEET_NAME, dtype=str, header=0)
    df_legend = df_legend.where(pd.notnull(df_legend), None)
    item_category_dict = df_legend.set_index('Key').T.to_dict('records')[0]
    return df_data_export.replace({ITEM_CATEGORY_HEADER: item_category_dict})



def apply_global_hierarchy(df_data_export: pd.DataFrame) -> pd.DataFrame:
    # Get the Product Line names from GH based on Material Group Name (MC0)
    df_data_export[MATERIAL_GROUP_HEADER] = df_data_export[MATERIAL_GROUP_HEADER].str.strip()
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=GLOBAL_HIERARCHY_SHEET_NAME, dtype=str, header=0,
                              usecols=[8, 38])
    df_data_export[GLOBAL_HIERARCHY_HEADER] = df_data_export.MAT_GROUP.map(
        df_legend.set_index(GH_MC0_HEADER)[GH_PRODUCT_LINE_HEADER])
    return df_data_export


def calculate_necessary_feature_fill(df_data_export: pd.DataFrame) -> pd.DataFrame:
    # Check & count if listed features from Necessary Feature List are included in Features List, which means that
    # those necessary are filled
    def check_if_necessary_filled(features, necessary_features):
        if necessary_features[0] == '':
            return 0

        ctr = 0
        for nf in necessary_features:
            if nf in features:
                ctr += 1
        #ctr = len(nf for nf in necessary_features if nf in features)
        return ctr / len(necessary_features)

    #df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] = '0'
    #df_data_export.loc[df_data_export[FEATURES_LIST_HEADER].isin([feature for feature in df_data_export[MAX_NECESSARY_FEATURES_LIST_HEADER].split(';')]), [NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER]] = '1'

    df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] = df_data_export.apply(
        lambda x: check_if_necessary_filled(x[FEATURES_LIST_HEADER].split(';'),
                                            x[MAX_NECESSARY_FEATURES_LIST_HEADER].split(';')), axis=1)

    return df_data_export


def apply_necessary_feature_mapping(df_data_export: pd.DataFrame) -> pd.DataFrame:
    # def necessary_feature_mapping(x):
    #     if float(x) == 1:
    #         return 'All necessary features filled'
    #     elif float(x) >= 0.75:
    #         return '75% - 99%'
    #     elif float(x) >= 0.5:
    #         return '50% - 74%'
    #     elif float(x) >= 0.25:
    #         return '25% - 49%'
    #     elif float(x) >= 0.1:
    #         return '1% - 24%'
    #     else:
    #         return 'No necessary features filled'

    # df_data_export['NEC_FILL'] = df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER].apply(
    #     lambda x: necessary_feature_mapping(x))

    df_data_export['NEC_FILL'] = 'No necessary features filled'

    df_data_export.loc[
        df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] == 1, ['NEC_FILL']] = 'All necessary features filled'
    df_data_export.loc[(df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] < 1) & (df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] >= 0.75), ['NEC_FILL']] = '75% - 99%'
    df_data_export.loc[(0.75 > df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER]) & (df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] >= 0.5), ['NEC_FILL']] = '50% - 74%'
    df_data_export.loc[(0.5 > df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER]) & (df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] >= 0.25), ['NEC_FILL']] = '25% - 49%'
    df_data_export.loc[(0.25 > df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER]) & (df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] >= 0.1), ['NEC_FILL']] = '1% - 24%'
    df_data_export.loc[
        df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] < 0.1, ['NEC_FILL']] = 'No necessary features filled'
    return df_data_export


def drop_necessary_features_list_column(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_data_export.drop(MAX_NECESSARY_FEATURES_LIST_HEADER, axis=1, inplace=True)
    return df_data_export


def get_list_of_vendors_from_gsh(df_data_export: pd.DataFrame) -> pd.DataFrame:
    # Load List of Vendors
    gsh_file = pd.ExcelFile(GSH_FILE_NAME)
    for sheet_name in gsh_file.sheet_names:
        if LIST_OF_VENDOR_PHRASE in sheet_name.lower():
            df_gsh = pd.read_excel(GSH_FILE_NAME, sheet_name=sheet_name, usecols=[0, 8], dtype=str).drop_duplicates()
            df_data_export[DATA_EXPORT_VENDOR_TYPE_HEADER] = df_data_export.VENDORC.map(
                df_gsh.set_index(GSH_VENDOR_HEADER)[GSH_VENDOR_TYPE_HEADER])
    return df_data_export


def get_person_responsible(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=GSH_SHEET_NAME, dtype=str, header=0)
    df_data_export[PIM_PERSON_RESPONSIBLE_HEADER] = df_data_export[GROUP_SUPPLIER_NAME_HEADER].map(
        df_legend.set_index(GROUP_SUPPLIER_NAME_HEADER)[PIM_PERSON_RESPONSIBLE_HEADER])
    return df_data_export


def set_product_status(df_data_export: pd.DataFrame) -> pd.DataFrame:
    def apply_other_mappings(x):
        if x[SALES_STATUS_HEADER] != '' and df_legend.loc[
                df_legend[SALES_STATUS_HEADER] == x[SALES_STATUS_HEADER], int(x[SALES_ORG_HEADER])].values[0] == 'O':
            return NON_ACTIVE_STATUS
        elif x['PARENTID'] == 'NotToBeClassified':
            return NON_ACTIVE_STATUS
        # Baltics
        elif x[SALES_ORG_HEADER] in ['3100', '3500', '4000']:
            if x['PARENTID'] in ['ERP_unclassified', 'WaitingNewClass']:
                return NON_ACTIVE_STATUS
            if 'dummy' in x['ITEMCATGROUP']:
                return NON_ACTIVE_STATUS
            if x['SAPCODE'].startswith(('A', 'C', 'G', 'H')):  # x['SAPCODE'].str.contains('^(A|C|G|H)', regex=True):
                return NON_ACTIVE_STATUS
        # Norway
        elif x[SALES_ORG_HEADER] == '2000':
            if 'dummy' in x['ITEMCATGROUP']:
                return NON_ACTIVE_STATUS
            if x['ITEMCATGROUP'] in ['Direct sales', 'Standard item', 'Cross dock border relevant',
                                     'Sales BOM, Pricing']:
                return NON_ACTIVE_STATUS
            if x['SAPCODE'].startswith(
                    ('PDD', 'SER', 'PAC')):  # x['SAPCODE'].str.contains('^(PDD|SER|PAC)', regex=True):
                return NON_ACTIVE_STATUS
            if x['SELL_ONN'] == 'archived':
                return NON_ACTIVE_STATUS
        # Sweden
        elif x[SALES_ORG_HEADER] == '1500':
            if x['PARENTID'] == 'ERP_unclassified':
                return NON_ACTIVE_STATUS
            if 'dummy' in x['ITEMCATGROUP']:
                return NON_ACTIVE_STATUS
            if x['ITEMCATGROUP'] in ['Sales BOM, Pricing', 'ATO item']:
                return NON_ACTIVE_STATUS
            if x['SAPCODE'].startswith(
                    ('PDD', 'SER', 'PAC', 'X', 'V')):  # x['SAPCODE'].str.contains('^(PDD|SER|PAC|X|V)', regex=True):
                return NON_ACTIVE_STATUS
            if 'X20' in x['PROD_RESP_SAP'] or 'X21' in x[
                'PROD_RESP_SAP']:  # x['PROD_RESP_SAP'].str.contains(['X20|X21'], na=False):
                return NON_ACTIVE_STATUS
        # Finland
        elif x[SALES_ORG_HEADER] == '1000':
            if x['PARENTID'] in ['ERP_unclassified', 'WaitingNewClass']:
                return NON_ACTIVE_STATUS
            if x['ITEMCATGROUP'] in ['Direct sales', 'Standard item', 'Sales BOM, Pricing', 'Cross Dock']:
                return NON_ACTIVE_STATUS
            if '1002' not in x['PROD_RESP']:  # x['PROD_RESP'].str.contains('1002', na=False):
                return NON_ACTIVE_STATUS
        # Poland
        elif x[SALES_ORG_HEADER] == '2500':
            if x['SAPCODE'].startswith(('PDD', 'SER', 'PAC', 'PDF',
                                        'XP')):  # x['SAPCODE'].str.contains('^(PDE|SER|PAC|PDF|XP)', regex=True):
                return NON_ACTIVE_STATUS
            if x['ITEMCATGROUP'] in ['Standard item', 'Cross Dock']:
                return NON_ACTIVE_STATUS
            if x['PROD_RESP'] == 'B':
                return NON_ACTIVE_STATUS
        return 'Active'

    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name='MD', dtype=str, header=0)

    df_data_export['Product status'] = df_data_export.apply(
        lambda x: apply_other_mappings(x), axis=1)

    return df_data_export


def set_product_status_vectorized(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_data_export['Product status'] = 'Active'

    df_data_export.loc[df_data_export['PARENTID'] == 'NotToBeClassified', ['Product status']] = NON_ACTIVE_STATUS

    # Sales Status table included in each country

    # Baltics
    df_data_export.loc[(df_data_export[SALES_ORG_HEADER].isin(['3100', '3500', '4000'])) & (
            (df_data_export['PARENTID'].isin(['ERP_unclassified', 'WaitingNewClass'])) | (
            'dummy' in df_data_export['ITEMCATGROUP']) | (
                df_data_export['SAPCODE'].str.startswith(('A', 'C', 'G', 'H'))) | (df_data_export['SALESSTATUS'].isin(
        ['Z6', 'ZZ', 'Dummy codes']))), [
                           'Product status']] = NON_ACTIVE_STATUS
    # Norway
    df_data_export.loc[(df_data_export[SALES_ORG_HEADER] == '2000') & (
            ('dummy' in df_data_export['ITEMCATGROUP']) | (df_data_export['ITEMCATGROUP'].isin(
        ['Direct sales', 'Standard item', 'Cross dock border relevant', 'Sales BOM, Pricing'])) | (
                df_data_export['SAPCODE'].str.startswith(('PDD', 'SER', 'PAC'))) | (df_data_export[
                                                                                        'SELL_ONN'] == 'archived') |
            (df_data_export['SALESSTATUS'].isin(['Z6', 'ZC', 'ZL', 'ZZ', 'Dummy codes']))), [
                           'Product status']] = NON_ACTIVE_STATUS
    # Sweden
    df_data_export.loc[
        (df_data_export[SALES_ORG_HEADER] == '1500') & ((df_data_export['PARENTID'] == 'ERP_unclassified') |
                                                        ('dummy' in df_data_export['ITEMCATGROUP']) | (
                                                            df_data_export['ITEMCATGROUP'].isin(
                                                                ['Sales BOM, Pricing', 'ATO item'])) | (
                                                            df_data_export['SAPCODE'].str.startswith(
                                                                ('PDD', 'SER', 'PAC', 'X', 'V'))) | (
                                                            df_data_export['PROD_RESP_SAP'].isin(['X21', 'X20'])) |
                                                        (df_data_export['SALESSTATUS'].isin(
                                                            ['Z4', 'Z6', 'ZC', 'ZZ', 'Dummy codes']))), [
            'Product status']] = NON_ACTIVE_STATUS
    # Finland --> MUSISZ DODAĆ 1002 PLANT, INNE NIŻ 1002 --> NON ACTIVE
    df_data_export.loc[
        (df_data_export[SALES_ORG_HEADER] == '1000') & (
                (df_data_export['PARENTID'].isin(['ERP_unclassified', 'WaitingNewClass'])) |
                (~df_data_export['ITEMCATGROUP'].isin(
                    ['Direct sales', 'Standard item', 'Sales BOM, Pricing', 'Cross Dock'])) |
                (df_data_export['SALESSTATUS'].isin(['Z4', 'Z6', 'ZB', 'ZC', 'ZI', 'ZL', 'ZZ', 'Dummy codes'])) | (df_data_export['PROD_RESP'] != '1002')), [
            'Product status']] = NON_ACTIVE_STATUS
    # Poland
    df_data_export.loc[(df_data_export[SALES_ORG_HEADER] == '2500') & (
            (df_data_export['ITEMCATGROUP'].isin(['Standard item', 'Cross Dock'])) | (
        df_data_export['SAPCODE'].str.startswith(('PDD', 'SER', 'PAC', 'PDF', 'XP'))) |
            (df_data_export['PROD_RESP'] == 'B') |
            (df_data_export['SALESSTATUS'].isin(['Z6', 'Z7', 'ZG', 'ZH', 'Dummy codes']))), [
                           'Product status']] = NON_ACTIVE_STATUS

    return df_data_export


def apply_phase_number(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_data_export['Phase'] = 'Other'

    gsh_file = pd.ExcelFile(LEGEND_FILE_NAME)
    for sheet_name in gsh_file.sheet_names:
        if 'PH' in sheet_name:
            df_ph = pd.read_excel(LEGEND_FILE_NAME, sheet_name=sheet_name, usecols=[0, 1], dtype=str)
            df_data_export = df_data_export.merge(df_ph, on=['SALESORG', 'PIMID'], how='left', indicator='exists')
            df_data_export['Phase'] = np.where(df_data_export['exists'] == 'both', sheet_name, df_data_export['Phase'])
            df_data_export = df_data_export.drop('exists', axis=1)

    return df_data_export


def exclude_products(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_exclusions = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name='Exclusions', dtype=str, header=0, usecols=[0, 1])
    df_data_export = pd.concat([df_data_export, df_exclusions, df_exclusions]).drop_duplicates(keep=False)

    return df_data_export


def label_own_brand_products(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_own_brand = pd.read_excel(LEGEND_FILE_NAME, sheet_name='Own Brand', usecols=[0], dtype=str)
    df_data_export = df_data_export.merge(df_own_brand, on=['PIMID'], how='left', indicator='exists')
    df_data_export['Phase'] = np.where(df_data_export['exists'] == 'both', 'Own Brand', df_data_export['Phase'])
    df_data_export = df_data_export.drop('exists', axis=1)

    return df_data_export

def calculate_necessary_feature_fill(df_data_export: pd.DataFrame) -> pd.DataFrame:
    def check_if_necessary_filled(features, necessary_features):
        if necessary_features[0] == '':
            return 0

        ctr = 0
        for nf in necessary_features:
            if nf in features:
                ctr += 1
        return ctr / len(necessary_features)

    df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER] = df_data_export.apply(
        lambda x: check_if_necessary_filled(x[FEATURES_LIST_HEADER].split(';'), x[MAX_NECESSARY_FEATURES_LIST_HEADER].split(';')), axis=1)

    return df_data_export


def apply_necessary_feature_mapping(df_data_export: pd.DataFrame) -> pd.DataFrame:
    def necessary_feature_mapping(x):
        if float(x) == 1:
            return 'Necessary Feature filled in dupa'
        else:
            return 'Just dupa'

    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=NECESSARY_MAPPING_SHEET_NAME, dtype=str, header=None)
    df_legend = df_legend.where(pd.notnull(df_legend), None)
    df_data_export['NEC_FILL'] = df_data_export[NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER].apply(lambda x: necessary_feature_mapping(x))

    return df_data_export



def main():
    # Load cache exports to df
    df_data_cache_export = read_all_cache_data_exports()  # read_cache_data_export()

    # Exclude products from report based on list in legenda.xlsx
    df_data_export = exclude_products(df_data_cache_export)

    # Apply Item Category dictionary
    df_data_export = apply_item_category_dictionary(df_data_export)

    # Product Line z Global Hierarchy
    df_data_export = apply_global_hierarchy(df_data_export)

    # Necessary Features filled in numbers
    df_data_export = calculate_necessary_feature_fill(df_data_export)

    # Necessary Feature mapping
    df_data_export = apply_necessary_feature_mapping(df_data_export)

    # Remove column with list of necessary features from cache
    df_data_export = drop_necessary_features_list_column(df_data_export)

    # Read stuff from GSH (e.g. Local / Multi)
    df_data_export = get_list_of_vendors_from_gsh(df_data_export)

    # Get PIM SC Person Responsible
    df_data_export = get_person_responsible(df_data_export)

    # Apply other mappings per country
    df_data_export = set_product_status_vectorized(df_data_export)  # set_product_status(df_data_export)

    # Apply phase number
    df_data_export = apply_phase_number(df_data_export)

    # Label Own Brand products
    df_data_export = label_own_brand_products(df_data_export)

    todayDate = dt.date.today().strftime('%Y-%m-%d')

    # Save active products export
    df_active = df_data_export.loc[df_data_export['Product status'] == 'Active']
    df_active.to_csv(f'reports/{todayDate}_active_data_export.csv', index=False)

    # Save non-active products export
    df_non_active = df_data_export.loc[df_data_export['Product status'] == NON_ACTIVE_STATUS]
    df_non_active.to_csv(f'reports/{todayDate}_non_active_data_export.csv', index=False)

    #df_data_export = apply_global_hierarchy(df_data_export)

    # Necessary Features filled in numbers
    df_data_export = calculate_necessary_feature_fill(df_data_export)

    # Necessary Feature mapping
    df_data_export = apply_necessary_feature_mapping(df_data_export)
    pass



if __name__ == "__main__":
    start = time.time()
    main()
    print("Czas:", time.time() - start)
