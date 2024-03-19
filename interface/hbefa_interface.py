import pyodbc
import os

def get_result_table(concept, fuel_type, traffic_situation):
    concept_table_mapping = {
        "CO": "EFA_HOT_Concept_CO_Ergebnisse",
        "CO2": "EFA_HOT_Concept_CO2_Rep_Ergebnisse",
        "FC": "EFA_HOT_Concept_FC_MJ_Ergebnisse",
        "HC": "EFA_HOT_Concept_HC_Ergebnisse",
        "Methan": "EFA_HOT_Concept_Methan_Ergebnisse",
        "mKr": "EFA_HOT_Concept_mKr_Ergebnisse",
        "Nox": "EFA_HOT_Concept_Nox_Ergebnisse",
        "PM": "EFA_HOT_Concept_PM_Ergebnisse",
    }
    result = []
    file_path = os.path.abspath(os.getcwd()) + "\HBEFA42_User.MDB"
    dbconn = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + file_path + r';'
    )
    cursor = dbconn.cursor()
    tablename = concept_table_mapping.get(concept, "CO")
    sql = '''
    SELECT EFA_weighted
    FROM {}
    WHERE EmConcept = ?
    AND TrafficSit = ?
    '''
    cursor.execute(sql.format(tablename), (fuel_type, traffic_situation))
    for row in cursor.fetchall():
        result.append(row.EFA_weighted)
    dbconn.close()
    return result
