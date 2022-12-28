import pandas as pd
import collections as co


DATA_EXPORT_FILE_NAME: str = '2022-12-28_data_export.csv'
LEGEND_FILE_NAME: str = 'legenda.xlsx'

# Sheet names
ITEM_CATEGORY_SHEET_NAME: str = 'Item Category'
GLOBAL_HIERARCHY_SHEET_NAME: str = 'GH'

#

# Headers
ITEM_CATEGORY_HEADER: str = 'ITEMCATGROUP'
GLOBAL_HIERARCHY_HEADER: str = 'Product Line'
MATERIAL_GROUP_HEADER: str = 'MAT_GROUP'
GH_MC0_HEADER: str = 'NEW ID MC0, GH 2020'
GH_PRODUCT_LINE_HEADER: str = 'Product line whole sale EN'
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

def main():
    # load cache export to df
    df_data_cache_export = read_cache_data_export()

    # apply Item Category dictionary
    df_data_export = apply_item_category_dictionary(df_data_cache_export)

    df_data_export = apply_global_hierarchy(df_data_export)

    pass


if __name__ == "__main__":
    main()