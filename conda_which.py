import conda.plugins
import argparse
import subprocess
import json
import os
from pathlib import Path
from prettytable import PrettyTable

def parse_conda_list_output(data):
    if 'error' in data:
        print(f"Error in command: {data['error']}")
        return {}
    else:
        packages = {pkg['name']: pkg['version'] for pkg in data}
        return packages

def conda_which(argv: list):
    parser = argparse.ArgumentParser("conda which")
    parser.add_argument("package", type=str, help="Name of the package")
    parser.add_argument("--timeout", type=int, default=None, help="Timeout for each environment check in seconds (default is no timeout)")
    args = parser.parse_args(argv)

    completed_process = subprocess.run(["conda", "env", "list", "--json"], capture_output=True, text=True)
    env_data = json.loads(completed_process.stdout)
    environments = env_data['envs']

    conda_root_path = Path(os.environ.get('CONDA_PREFIX')).parent.parent

    installed_envs = []
    for env in environments:
        if str(env) == str(conda_root_path):
            print(f"Checking: {env} (base)")
        else:
            print(f"Checking: {env}")
        try:
            result = subprocess.run(['conda', 'list', '--prefix', env, '--json'], capture_output=True, text=True, timeout=args.timeout)
            data = json.loads(result.stdout)
            packages = {pkg['name']: pkg['version'] for pkg in data}
            if args.package in packages:
                installed_envs.append(env)
        except subprocess.TimeoutExpired:
            print(f"Skipping environment {env} due to timeout")
    
    print("========================")
    if installed_envs:    
        print(f"The package '{args.package}' is installed in the following environments:")
        table = PrettyTable()
        table.field_names = ["Environment Name", "Environment Path"]
        table.align["Environment Name"] = 'l'
        table.align["Environment Path"] = 'l'
        for env in installed_envs:
            env_path = Path(env)
            if env_path == conda_root_path:
                table.add_row(["base", str(conda_root_path)])
            else:
                table.add_row([env_path.name, str(env_path)])
        print(table)
    else:
        print(f"The package '{args.package}' is not installed in any environment")

@conda.plugins.hookimpl
def conda_subcommands():
    yield conda.plugins.CondaSubcommand(
        name="which",
        summary="Which environments have <package> installed?",
        action=conda_which,
    )
