from argparse import ArgumentParser
from os import environ as environment_variables

from .utils import random_hex

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
    'first_admin_password': [
        ['first-admin-password'],
        ['FIRST_ADMIN_PASSWORD', 'ML_FAP'],
        random_hex(10)
    ],
    'jwt_secret': [
        ['jwt-secret'],
        ['JWT_SECRET', 'ML_JWT_SECRET'],
        random_hex(20)
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

    return vars(parser.parse_known_args()[0])


# Retrieve the best parameter with this priority:
# arguments, environment variables, default value
def get_parameter(name: str) -> str:
    parsed_args = get_args()
    parameter = PARAMETERS[name]
    args = parameter[0]
    envs = parameter[1]
    default = parameter[2]

    for arg in args:
        value = parsed_args[arg.replace('-', '_')]
        if value:
            return value
    for env in envs:
        if env in environment_variables:
            return environment_variables[env]
    return default
