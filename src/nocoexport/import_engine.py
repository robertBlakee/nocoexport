import sqlite3
import pandas as pd
from os import path
from .functions import table_export, ID_validation, base_prefix_validation


def import_engine(base_exp, base_tar):
    # Connect to config data base
    base_cfg = sqlite3.connect(path.dirname(__file__)+"/config.db")

    # Base prefix validation
    base_prefix_validation(base_exp, base_tar)

    # Get base prefix and id
    answer = pd.read_sql_query("SELECT prefix, id FROM nc_bases_v2", base_exp)
    base_ID = answer['id'][0]
    base_prefix = answer['prefix'][0]
    # Get base tables list (without relations tables)
    base_tab_list = pd.read_sql_query("SELECT table_name AS name FROM nc_models_v2 WHERE mm=0", base_exp)
    # Get base manyToMany relation tables list
    rel_tab_list = pd.read_sql_query("SELECT table_name AS name FROM nc_models_v2 WHERE mm=1", base_exp)
    # Get system tables list (all without starts with base_prefix)
    sys_tab_list = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '{base_prefix+'%'}'", base_exp)

    # Enter target base user to exported base
    user_ID = pd.read_sql_query("SELECT id FROM nc_users_v2", base_tar)
    user_ID = user_ID['id'][0]
    base_exp.execute(f"UPDATE nc_base_users_v2 SET fk_user_id='{user_ID}' WHERE base_id='{base_ID}'")
    base_exp.commit()

    # ID validation
    ID_validation(sys_tab_list['name'], base_exp, base_tar, base_cfg)

    # Import base tables
    table_export(base_tab_list['name'], base_exp, base_tar, if_create_schema=True)
    # Import system tables
    table_export(sys_tab_list['name'], base_exp, base_tar)
    # Import relations tables
    table_export(rel_tab_list['name'], base_exp, base_tar, if_create_schema=True)

    # Close base connection
    base_cfg.close()
