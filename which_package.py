
import conda.plugins
import argparse
import conda.cli.python_api
import re

def parse_conda_list_output(output):
    packages = {}
    for line in output.split('\n'):
        if line:
            name, version, *_ = line.split()
            packages[name] = version
    return packages

def which_package(argv: list):
    parser = argparse.ArgumentParser()

    parser.add_argument("package", type=str, help="Name of the package")

    args = parser.parse_args(argv)

    environments = conda.cli.python_api.run_command(conda.cli.python_api.Commands.INFO, "--envs")[0]
    environments = re.findall(r'([a-zA-Z0-9_\-\.\/]+)  \*', environments)  # include base env

    installed_envs = []
    for env in environments:
        output, error, return_code = conda.cli.python_api.run_command(conda.cli.python_api.Commands.LIST, "-n", env)
        packages = parse_conda_list_output(output)
        if args.package in packages:
            installed_envs.append(env)

    print(f"The package '{args.package}' is installed in the following environments:")
    for env in installed_envs:
        print(env)

@conda.plugins.hookimpl
def conda_subcommands():
    yield conda.plugins.CondaSubcommand(
        name="which",
        summary="Takes a package name and returns a list of environments where the package is installed",
        action=which_package,
    )
