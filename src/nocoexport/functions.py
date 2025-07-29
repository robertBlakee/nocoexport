import pandas as pd
import string
import random


# Export table from one base to other
def table_export(table_name_list: list, base_src, base_tar, if_create_schema: bool = False, conditions: str = ""):
    for table_name in table_name_list:
        # Get table schema and create empty table with that
        if if_create_schema:
            schema = pd.read_sql_query(f"SELECT sql FROM sqlite_master WHERE type = 'table' AND name = '{table_name}'", base_src)
            schema = schema.iloc[0][0]
            base_tar.execute(schema)
        # Insert data to new table
        data = pd.read_sql_query(f"SELECT * FROM {table_name} {conditions}", base_src, dtype_backend='numpy_nullable')
        data.to_sql(table_name, base_tar, index=False, if_exists='append')


# New ID generator from old ID
def generate_ID(old_ID):
    characters = string.ascii_lowercase + string.digits
    nr = ''.join(random.choice(characters) for i in range(14))
    prefix = old_ID[0:(len(old_ID)-14)]

    return prefix+nr


# New base prefix generator
def generate_base_prefix():
    characters = string.ascii_lowercase + string.digits
    nr = ''.join(random.choice(characters) for i in range(4))
    base_prefix = 'nc_'+nr+'__'

    return base_prefix


# Check for duplicates existing in data sets (is skipping none/null values)
# Returns data set with index and value of duplicates and placeholder to enter new value
def duplicates(data):
    data = pd.concat(data, axis=0, ignore_index=True)
    data = data.dropna()
    is_duplicate = data.duplicated(keep='last')
    duplicates_idx = is_duplicate[is_duplicate].index

    clones = [{'idx': clone_idx, 'old_ID': data[clone_idx], 'new_ID': ""} for clone_idx in duplicates_idx]
    clones = pd.DataFrame(clones)

    return clones


# Check given element value is unique for data set
def is_unique(element, datas: list):
    for data in datas:
        for one in data:
            if one == element:
                return False

    return True


# Check for duplicates and rename ID in given tables if it is necessery 
def ID_validation(table_names, base_exp, base_tar, base_cfg):
    table_cfg = pd.read_sql_query("SELECT * FROM systemTables", base_cfg)

    for table in table_names:
        # Get id column from table but if it does not exist continue
        try:
            table_exp = pd.read_sql_query(f"SELECT id FROM {table}", base_exp)
            table_tar = pd.read_sql_query(f"SELECT id FROM {table}", base_tar)
        except Exception:
            continue
        clones = duplicates([table_exp['id'], table_tar['id']])

        if not clones.empty:
            # Generate new ID for each duplicate and insert it into exported base
            for idx, clone in clones.iterrows():
                new_ID = generate_ID(clone['old_ID'])
                while not is_unique(new_ID, [table_exp['id'], table_tar['id']]):
                    new_ID = generate_ID(clone['old_ID'])

                clones['new_ID'][idx] = new_ID
                base_exp.execute(f"UPDATE {table} SET id='{new_ID}' WHERE id='{clone['old_ID']}'")
                base_exp.commit()

            # Check for and replace old_ID in other tables if ID names are not None
            ID_names = [table_cfg[table_cfg.table_name == table]["ID_name"].values[0]]
            if ID_names != [None]:
                ID_name_2 = table_cfg[table_cfg.table_name == table]["ID_name_2"].values[0]
                if ID_name_2 is not None:
                    ID_names.append(ID_name_2)

                for tab in table_names:
                    col_names = pd.DataFrame([])
                    for id_name in ID_names:
                        answer = pd.read_sql_query(f"SELECT name FROM PRAGMA_TABLE_INFO('{tab}') WHERE name LIKE '%{id_name}'", base_exp)
                        col_names = pd.concat([col_names, answer], axis=0, ignore_index=True)
                    for col in col_names['name']:
                        for index, clone in clones.iterrows():
                            base_exp.execute(f"UPDATE {tab} SET {col}='{clone['new_ID']}' WHERE {col}='{clone['old_ID']}'")
                            base_exp.commit()


# Check for duplicates and rename prefix in exported base if it is necessery
def base_prefix_validation(base_exp, base_tar):
    base_exp_old_prefix = pd.read_sql_query("SELECT prefix FROM nc_bases_v2", base_exp)['prefix'][0]
    base_tar_prefixList = pd.read_sql_query("SELECT prefix FROM nc_bases_v2", base_tar)['prefix']

    # Check prefix of exported base is unique for target base prefixes 
    if not is_unique(base_exp_old_prefix, [base_tar_prefixList]):
        # If not generate new prefix until it will be unique
        base_exp_new_prefix = generate_base_prefix()
        while not is_unique(base_exp_new_prefix, base_tar_prefixList):
            base_exp_new_prefix = generate_base_prefix()
    
        # Replace old prefix in nc_bases_v2 table
        base_exp.execute(f"UPDATE nc_bases_v2 SET prefix='{base_exp_new_prefix}' WHERE prefix='{base_exp_old_prefix}'")
        
        # Get table names grom nc_models_v2 table
        table_name = pd.read_sql_query(f"SELECT table_name AS name FROM nc_models_v2 WHERE table_name LIKE '{base_exp_old_prefix}%'", base_exp)['name']
        # Replace old prefix of table names in nc_models_v2 table
        for name in table_name:
            new_name = name.replace(base_exp_old_prefix, base_exp_new_prefix)
            base_exp.execute(f"UPDATE nc_models_v2 SET table_name='{new_name}' WHERE table_name='{name}'")
        base_exp.commit()

        # Get base tables list (including relation tables)
        base_tables = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{base_exp_old_prefix}%'", base_exp)['name']
        # Change base tables names to begins from new prefix
        for name in base_tables:
            new_name = name.replace(base_exp_old_prefix, base_exp_new_prefix)
            base_exp.execute(f"ALTER TABLE {name} RENAME TO {new_name}")
        base_exp.commit()