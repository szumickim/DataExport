import pandas as pd
import collections as co


DATA_EXPORT_FILE_NAME: str = '2022-12-28_data_export.csv'
LEGEND_FILE_NAME: str = 'legenda.xlsx'

# Sheet names
ITEM_CATEGORY_SHEET_NAME: str = 'Item Category'
GLOBAL_HIERARCHY_SHEET_NAME: str = 'GH'
NECESSARY_MAPPING_SHEET_NAME: str = 'Necessary Mapping'

#

# Headers
ITEM_CATEGORY_HEADER: str = 'ITEMCATGROUP'
GLOBAL_HIERARCHY_HEADER: str = 'Product Line'
MATERIAL_GROUP_HEADER: str = 'MAT_GROUP'
GH_MC0_HEADER: str = 'NEW ID MC0, GH 2020'
GH_PRODUCT_LINE_HEADER: str = 'Product line whole sale EN'
NECESSARY_FEATURE_FILLED_IN_NUMBER_HEADER: str = 'NECESSARY_FILL'
FEATURES_LIST_HEADER: str = 'FEATURES_COUNT'
MAX_NECESSARY_FEATURES_LIST_HEADER: str = 'MAX_NECESSARY_FEATURES_LIST'


def read_cache_data_export() -> pd.DataFrame:
    df = pd.read_csv(DATA_EXPORT_FILE_NAME, sep=',', dtype='string')
    return df.fillna('')


def apply_item_category_dictionary(df_cache: pd.DataFrame) -> pd.DataFrame:
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=ITEM_CATEGORY_SHEET_NAME, dtype=str, header=0)
    df_legend = df_legend.where(pd.notnull(df_legend), None)
    item_category_dict = df_legend.set_index('Key').T.to_dict('records')[0]
    return df_cache.replace({ITEM_CATEGORY_HEADER: item_category_dict})


def apply_global_hierarchy(df_data_export: pd.DataFrame) -> pd.DataFrame:
    df_data_export[MATERIAL_GROUP_HEADER] = df_data_export[MATERIAL_GROUP_HEADER].str.strip()
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name=GLOBAL_HIERARCHY_SHEET_NAME, dtype=str, header=0, usecols=[8, 38])
    df_data_export[GLOBAL_HIERARCHY_HEADER] = df_data_export.MAT_GROUP.map(df_legend.set_index(GH_MC0_HEADER)[GH_PRODUCT_LINE_HEADER])
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
    # load cache export to df
    df_data_cache_export = read_cache_data_export()

    # apply Item Category dictionary
    df_data_export = apply_item_category_dictionary(df_data_cache_export)

    # Product Line z Global Hierarchy
    #df_data_export = apply_global_hierarchy(df_data_export)

    # Necessary Features filled in numbers
    df_data_export = calculate_necessary_feature_fill(df_data_export)

    # Necessary Feature mapping
    df_data_export = apply_necessary_feature_mapping(df_data_export)
    pass


if __name__ == "__main__":
    main()