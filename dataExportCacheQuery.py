import pandas as pd
import pyodbc
import datetime as dt
import time

configasd = ('DRIVER={iSeries Access ODBC Driver};''SYSTEM=S780F1B0;''DATABASE=SL1CACHE;''UID=PLOCITOM;' # wpisz zamiast login swój login do webquery / data cache
             'PWD=liscrazy21;')


def get_the_data_from_Cache(query, start_row, iteration_rows):
    df_final = pd.DataFrame()

    cnxn = pyodbc.connect(configasd)

    while True:
        query_sql = query + f' OFFSET {start_row} ROW FETCH NEXT {iteration_rows} ROWS ONLY'

        df = pd.read_sql(query_sql, cnxn)
        if len(df.index) > 0:
            df_final = pd.concat([df_final, df], ignore_index=True)

            start_row += iteration_rows
            print(f'Liczba przeprocesowanych wierszy: {start_row}')
        else:
            break

        # if start_row > 60:
        #     break

    todayDate = dt.date.today().strftime('%Y-%m-%d')
    df_final.to_csv(f'{todayDate}_data_export.csv', index=False)


if __name__ == '__main__':
    start = time.time()

    # data export
    query = '''SELECT * FROM MDMPLTEAM.ACTIVE_DATA_EXPORT WHERE SALESORG = '1000' '''
    get_the_data_from_Cache(query, 0, 10000)

    # test norway vendors
    # query = 'SELECT * FROM MDMPLTEAM.NORWAYVENDORS'
    # get_the_data_from_Cache(query, 0, 10)

    print("Czas:", time.time() - start)