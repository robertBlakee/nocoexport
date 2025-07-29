import pandas as pd
import sqlite3
from os import path
from .functions import table_export


def export_engine(base_src, base_exp, base_ID):
    # Connect to bases
    base_cfg = sqlite3.connect(path.dirname(__file__)+"/config.db")

    # Load system tables list to export
    sys_tab_list = pd.read_sql_query("SELECT table_name FROM systemTables WHERE toExport=1", base_cfg)
    # Get exported base ID and prefix
    base_info = pd.read_sql_query(f"SELECT id, prefix FROM nc_bases_v2 WHERE id='{base_ID}'", base_src)
    # Get base tables list
    params = base_info['prefix'][0] + '%'
    base_tab_list = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{params}'", base_src)

    # Export base tables
    table_export(base_tab_list['name'], base_src, base_exp, True)
    # Export 'nc_bases_v2'
    table_export(['nc_bases_v2'], base_src, base_exp, False, f"WHERE id='{base_info['id'][0]}'")
    # Export rest of system tables
    table_export(sys_tab_list['table_name'], base_src, base_exp, False, f"WHERE base_id='{base_info['id'][0]}'")

    # Close base connectes
    base_cfg.close()
