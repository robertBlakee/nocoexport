Program allows export database directly from one nocoDB instance to another or file. You need know dir to noco file ('noco.db') of your nocoDB app. This file
contains all app data including databases. Dir is specifies while 'run docker' command.

positional arguments {list,export,import,move}:
  - nocoexport list [-h] srcBase_path:
        List titles of bases belong to given noco file

        positional arguments:
          srcBase_path  Path to noco file
      
  - nocoexport export [-h] srcBase_path baseTitle:
        Export base from given noco file to exportedBase.db file

        positional arguments:
          srcBase_path  Path to noco file that contains base to export
          baseTitle     Title of base to export

  - nocoexport import [-h] expBase_path tarBase_path:
        Import base from file created with 'export' function to noco file

        positional arguments:
          expBase_path  Path to file created with 'export' function use,
                        that contains base to import
          tarBase_path  Path to target noco file that is importing base
          
  - nocoexport move [-h] srcBase_path tarBase_path baseTitle:
        Move base directly from one noco file to another

        positional arguments:
          srcBase_path  Path to noco file that contains base to export
          tarBase_path  Path to target noco file that is importing base
          baseTitle     Title of base to export
