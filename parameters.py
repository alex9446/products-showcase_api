from argparse import ArgumentParser
from os import environ as environment_variables

# PARAMETERS SCHEME
# 'parameter_name': [
#     ['cli-argument', ...],
#     ['ENVIRONMENT_VARIABLE', ...],
#     'default value'
# ]

PARAMETERS = {
    'allowed_cors': [
        ['allowed-cors'],
        ['ALLOWED_CORS', 'ML_CORS'],
        ''
    ],
    'database_url': [
        ['database-url'],
        ['DATABASE_URL', 'ML_DB_URL'],
        'sqlite:///db.sqlite'
    ],
    'port': [
        ['port'],
        ['PORT', 'ML_PORT'],
        '8080'
    ]
}


# CLI argument parser
def get_args() -> dict:
    total_arguments = []
    for values in PARAMETERS.values():
        total_arguments.extend(values[0])

    parser = ArgumentParser()

    for argument in total_arguments:
        parser.add_argument(f'--{argument}')

    return vars(parser.parse_args())


# Retrieve the best parameter with this priority:
# arguments, environment variables, default value
def get_parameter(name: str) -> str:
    parsed_args = get_args()
    parameter = PARAMETERS[name]
    args = parameter[0]
    envs = parameter[1]
    default = parameter[2]

    for arg in args:
        value = parsed_args[arg]
        if value:
            return value
    for env in envs:
        if env in environment_variables:
            return environment_variables[env]
    return default
