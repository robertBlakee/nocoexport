import argparse
from .main import list_bases, export_base, import_base, move_base


# Command line interface handler
def cli():
    # Add argument parser for command line interface
    parser = argparse.ArgumentParser(
        prog="nocoexport",
        description="Program allows export database directly from one nocoDB instance to another or file. "
                    "You need know dir to noco file ('noco.db') of your nocoDB app. This file contains all app data including databases. "
                    "Dir is specifies while 'run docker' command."
    )
    subparsers = parser.add_subparsers(dest="function")

    parser_list = subparsers.add_parser("list", description="List titles of bases belong to given noco file")
    parser_list.add_argument("source", help="Path to noco file")

    parser_export = subparsers.add_parser("export", description="Export base from given noco file to exportedBase.db file")
    parser_export.add_argument("source", help="Path to noco file that contains base to export")
    parser_export.add_argument("title", help="Title of base to export")

    parser_import = subparsers.add_parser("import", description="Import base from file created with 'export' function to noco file")
    parser_import.add_argument("source", help="Path to file created with 'export' function use, that contains base to import")
    parser_import.add_argument("target", help="Path to target noco file that is importing base")

    parser_move = subparsers.add_parser("move", description="Move base directly from one noco file to another")
    parser_move.add_argument("source", help="Path to noco file that contains base to export")
    parser_move.add_argument("target", help="Path to target noco file that is importing base")
    parser_move.add_argument("title", help="Title of base to export")

    parsed_args = parser.parse_args()

    # Call specified function depend on terminal command
    match parsed_args.function:
        case 'list':
            list_bases(parsed_args.source)
        case 'export':
            export_base(parsed_args.source, parsed_args.title)
        case 'import':
            import_base(parsed_args.source, parsed_args.target)
        case 'move':
            move_base(parsed_args.source, parsed_args.target, parsed_args.title)
