Program allows export database directly from one nocoDB instance to another or file. You need know dir to noco file ('noco.db') of your nocoDB app. This file
contains all app data including databases. Dir is specifies while 'run docker' command.

positional arguments {list,export,import,move}:
  - nocoexport list [-h] source:
        List titles of bases belong to given noco file

        positional arguments:
          source    Path to noco file
      
  - nocoexport export [-h] source title:
        Export base from given noco file to exportedBase.db file

        positional arguments:
          source    Path to noco file that contains base to export
          title     Title of base to export

  - nocoexport import [-h] expBase_path target:
        Import base from file created with 'export' function to noco file

        positional arguments:
          source    Path to file created with 'export' function use,
                        that contains base to import
          target    Path to target noco file that is importing base
          
  - nocoexport move [-h] source target title:
        Move base directly from one noco file to another

        positional arguments:
          source    Path to noco file that contains base to export
          target    Path to target noco file that is importing base
          title     Title of base to export
