import pandas as pd
import collections as co


DATA_EXPORT_FILE_NAME: str = '2022-12-28_data_export.csv'
LEGEND_FILE_NAME: str = 'legenda.xlsx'
ITEM_CATEGORY_HEADER: str = 'ITEMCATGROUP'

def read_cache_data_export() -> pd.DataFrame:
    df = pd.read_csv(DATA_EXPORT_FILE_NAME, sep=',', dtype='string')
    df = df.fillna('')
    return df


def apply_item_category_dictionary(df_cache: pd.DataFrame) -> pd.DataFrame:
    df_legend = pd.read_excel(io=LEGEND_FILE_NAME, sheet_name='Item Category', dtype=str, header=0)
    df_legend = df_legend.where(pd.notnull(df_legend), None)
    item_category_dict = df_legend.set_index('Key').T.to_dict('records')[0]
    df_cache = df_cache.replace({ITEM_CATEGORY_HEADER: item_category_dict})
    return df_cache


def main():
    # load cache export to df
    df_data_cache_export = read_cache_data_export()

    # apply Item Category dictionary
    df_data_export = apply_item_category_dictionary(df_data_cache_export)

    pass


if __name__ == "__main__":
    main()