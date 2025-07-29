import pandas as pd
import sqlite3
import traceback
from os import path, remove
from urllib.request import pathname2url
from .export_engine import export_engine
from .import_engine import import_engine


# Show list of bases belong to specified noco file
def listBases(base_src_path):
    # Try connect to base and check data propriety
    try:
        base_src_url = "file:{}?mode=rw".format(pathname2url(base_src_path))
        base_src = sqlite3.connect(base_src_url, uri=True)
        bases_list = pd.read_sql_query("SELECT title FROM nc_bases_v2", base_src)
    except Exception:
        print("\n" + "Incorrect path or base file!" + "\n")
        return

    # Print bases list
    print(bases_list)
    base_src.close()


# Export base data from noco file to esported file
def exportBase(base_src_path, base_title):
    # Try connect to base and check data propriety
    try:
        base_src_url = "file:{}?mode=rw".format(pathname2url(base_src_path))
        base_src = sqlite3.connect(base_src_url, uri=True)
        pd.read_sql_query("SELECT title FROM nc_bases_v2", base_src)
    except Exception:
        print("\n" + "Incorrect path or base file!" + "\n")
        return

    # Check base with given title exist in file
    answer = pd.read_sql_query(
        f"SELECT id FROM nc_bases_v2 WHERE title='{base_title}'", base_src
    )
    if answer.empty:
        print("\n" + "Base with this title doesn't exist!" + "\n")
        return

    # Start export process
    try:
        # Create empty file for exported base
        base_exp = sqlite3.connect("exportedBase.db")
        # Call base export function
        export_engine(base_src, base_exp, base_title)
        print("\n" + "Base export completed!")
        print("Your base data are in 'exportedBase.db' file")
    except Exception:
        print("Error while export process")

    base_exp.close()
    base_src.close()


# Import base data from exported file to noco file
def importBase(base_exp_path, base_tar_path):
    # Try connect to base and check data propriety
    try:
        base_exp_url = "file:{}?mode=rw".format(pathname2url(base_exp_path))
        base_exp = sqlite3.connect(base_exp_url, uri=True)
        pd.read_sql_query("SELECT title FROM nc_bases_v2", base_exp)
    except Exception:
        print("\n", "Incorrect path or file of exported base (first argument)!", "\n")
        return
    try:
        base_tar_url = "file:{}?mode=rw".format(pathname2url(base_tar_path))
        base_tar = sqlite3.connect(base_tar_url, uri=True)
        pd.read_sql_query("SELECT title FROM nc_bases_v2", base_tar)
    except Exception:
        print("\n", "Incorrect path or file of target base (second argument)!", "\n")
        return

    # Check base with the same title exists in target file
    base_exp_title = pd.read_sql_query("SELECT title FROM nc_bases_v2", base_exp)["title"][0]
    answer = pd.read_sql_query(f"SELECT id FROM nc_bases_v2 WHERE title='{base_exp_title}'", base_tar)
    if not answer.empty:
        print("Base with given title already exists in target file")
        return

    # Start import process
    try:
        # Call base import function
        import_engine(base_exp, base_tar)
        print("\n", "Base import completed!")
    except Exception:
        print("Error while import process")

    base_exp.close()
    base_tar.close()


# Move base data from one noco file to another
def moveBase(base_src_path, base_tar_path, base_title):
    # Connect to bases and check data propriety
    try:
        base_src_url = "file:{}?mode=rw".format(pathname2url(base_src_path))
        base_src = sqlite3.connect(base_src_url, uri=True)
        pd.read_sql_query("SELECT title FROM nc_bases_v2", base_src)
    except Exception:
        print("\n", "Incorrect path or file of source base (first argument)!", "\n")
        return
    try:
        base_tar_url = "file:{}?mode=rw".format(pathname2url(base_tar_path))
        base_tar = sqlite3.connect(base_tar_url, uri=True)
        pd.read_sql_query("SELECT title FROM nc_bases_v2", base_tar)
    except Exception:
        print("\n", "Incorrect path or file of target base (second argument)!", "\n")
        return

    # Check base with given title exists in source file
    answer = pd.read_sql_query(f"SELECT id FROM nc_bases_v2 WHERE title='{base_title}'", base_src)
    if answer.empty:
        print("\n", "Base with this title doesn't exist!", "\n")
        return
    # Check base with the same title exists in target file
    answer = pd.read_sql_query(f"SELECT id FROM nc_bases_v2 WHERE title='{base_title}'", base_tar)
    if not answer.empty:
        print("Base with given title already exists in target file")
        return

    # Start moving process
    try:
        # Create empty file for exported base
        base_exp = sqlite3.connect(path.dirname(__file__) + "/exportedBase.db")
        # Call base export function
        export_engine(base_src, base_exp, base_title)
        # Call base import function
        import_engine(base_exp, base_tar)
        print("\n", "Base moving completed!")
        
    except Exception:
        print("Error while export or import process")
        traceback.print_exc()

    remove(path.dirname(__file__) + "/exportedBase.db")
    base_src.close()
    base_tar.close()
    base_exp.close()
