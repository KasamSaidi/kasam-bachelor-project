import pyodbc


def connect_to_hbefa():
    pyodbc.pooling = False
    dbconn = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Program Files (x86)\HBEFA\HBEFA 4.2\program\HBEFA42_Prog.accde;'
    )
    cursor = dbconn.cursor()
    tablename = "B_EFA_NonReg_Poll_per_vehkm"
    sql = f'select * from "{tablename}"'
    cursor.execute(sql)
    for row in cursor.description:
        print(row)
        print("----------------------------------------------------------------------------------------------")

def get_result_table(concept):
    concept_table_mapping = {
        "CO": "EFA_HOT_Concept_CO_Ergebnisse",
        "CO2": "EFA_HOT_Concept_CO2_Rep_Ergebnisse",
        "FC": "EFA_HOT_Concept_FC_MJ_Ergebnisse",
        "HC": "EFA_HOT_Concept_HC_Ergebnisse",
        "Methan": "EFA_HOT_Concept_Methan_Ergebnisse",
        "mKr": "EFA_HOT_Concept_mKr_Ergebnisse",
        "Nox": "EFA_HOT_Concept_Nox_Ergebnisse",
        "Pb": "EFA_HOT_Concept_Pb_Ergebnisse",
        "PM": "EFA_HOT_Concept_PM_Ergebnisse",
    }
    result = []
    dbconn = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Desktop\BACHELOR\HBEFA\hbefa64\HB42_DB_files_64bit\user\HBEFA42_User.MDB;'
    )
    cursor = dbconn.cursor()
    tablename = concept_table_mapping.get(concept, "CO")
    # quieries für fuel_type und traffic status#+
    sql = f'''
    SELECT EFA_weighted
    FROM "{tablename}"
    WHERE (EmConcept = 'D' or EmConcept = 'B (4T)')
    AND TrafficSit = 'Agglo/AB-Nat./80/dicht'
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        result.append(row)
    dbconn.close()
    return result
