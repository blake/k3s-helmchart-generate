#!/usr/bin/env python3
# Copyright (c) 2019 Blake Covarrubias
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Helper script to generate HelmChart CRDs for use with k3s"""

import argparse
from typing import TypedDict

import yaml


class LiteralStr(str):
    """Literal string class. Inherits from str class."""

class Specification(TypedDict, total=False):
    """
    A specification object for the Specification field of the HelmChart CRD.

    See https://rancher.com/docs/k3s/latest/en/helm/#helmchart-field-definitions
    for a list of field definitions.
    """
    chart: str
    repo: str
    set: dict[str, str]
    targetNamespace: str
    valuesContent: LiteralStr
    version: str

class HelmChart(TypedDict):
    """
    A HelmChart resource object.
    """
    apiVersion: str
    kind: str
    metadata: dict[str, str]
    spec: Specification


def literal_representer(
    dumper: yaml.dumper.Dumper, data: LiteralStr
) -> yaml.nodes.ScalarNode:
    """
    PyYAML representer to format string as a literal string, multiline string with
    newlines preserved

    :param dumper: PyYAML dumper object
    :type dumper: class:`yaml.dumper.Dumper`
    :param data: LiteralStr string data
    :type data: class:`LiteralStr`

    :returns: A ScalarNode object for the new YAML representer
    :rtype: class:`yaml.nodes.ScalarNode`
    """
    # Return a scalar supporting literal YAML values ('|')  of type string (tag)
    # for values of type 'LiteralStr'
    return dumper.represent_scalar(style="|", tag="tag:yaml.org,2002:str", value=data)


# Use the literal_representer to serialize 'LiteralStr' data types
yaml.add_representer(data_type=LiteralStr, representer=literal_representer)


def parse_set_args(arguments: list[str]):
    """
    Parses --set arguments and combines them into a single dictionary

    :param arguments: List of set arguments specified on the CLI
    :type arguments: list

    :returns: A dictionary containing all defined set values
    :rtype: dict
    """
    set_dict: dict[str, str] = dict()
    for set_arg in arguments:
        # Parse comma-separated arguments
        arg_parts = set_arg.split(",")

        # Add each argument to set_dict
        for argument in arg_parts:
            key, value = argument.split("=")
            set_dict.update({key: value})

    return set_dict


def read_values_files(files: list[str]):
    """
    Reads contents of YAML valueFiles. Returns combined dictionary of values.

    :param files: List of valuesFiles specified on the CLI
    :type files: list

    :returns: A combined dictionary containing all values
    :rtype: dict
    """
    values: dict[str, str] = dict()
    for filename in files:
        content = yaml.safe_load(filename)
        values.update(content)

    return values


def generate_helmchart(arguments: argparse.Namespace):
    """
    Returns a dictionary object representing a HelmChart resource

    :param arguments: A :class:`argparse.Namespace` object
    :type arguments: class:`argparse.Namespace`

    :returns: A dictionary representing a HelmChart resource
    :rtype: dict
    """

    specification = Specification(chart=arguments.chart)

    if arguments.namespace:
        specification["targetNamespace"] = arguments.namespace
    if arguments.repo:
        specification["repo"] = arguments.repo
    if arguments.version:
        specification["version"] = arguments.version

    # Chart configuration variables
    if arguments.set:
        specification["set"] = parse_set_args(arguments.set)
    if arguments.values:
        values = read_values_files(arguments.values)
        values_str = LiteralStr(yaml.dump(data=values))
        specification["valuesContent"] = values_str

    helmchart = HelmChart(
        apiVersion="helm.cattle.io/v1",
        kind="HelmChart",
        metadata={
            "name": arguments.name,
            "namespace": arguments.helmcontroller_namespace,
        },
        spec=specification
    )

    return helmchart


def parse_arguments():
    """
    Parse arguments provided by the command line.
    """
    parser = argparse.ArgumentParser(
        description=("This command generates K3s HelmChart resource manifests")
    )

    # Positional arguments
    parser.add_argument("chart", metavar="CHART", help="A chart reference or a URL")

    parser.add_argument("--name", required=True, help="Name of the chart")
    parser.add_argument(
        "--repo", help="chart repository URL where to locate the requested chart"
    )
    parser.add_argument(
        "--version",
        help=(
            "Specify the exact chart version to install. If this is not "
            "specified, the latest version is installed"
        ),
    )

    parser.add_argument(
        "--helmcontroller-namespace",
        "--tiller-namespace",
        default="kube-system",
        help='Namespace of Helm Controller (default "kube-system")',
    )

    parser.add_argument(
        "--namespace",
        "--target-namespace",
        metavar="TARGET_NAMESPACE",
        help=(
            "Namespace to install the release into. Defaults to the Helm "
            "Controller namespace."
        ),
    )

    parser.add_argument(
        "--set",
        "--set-string",
        action="append",
        help=(
            "Set values on the command line (can specify multiple or separate"
            " values with commas: key1=val1,key2=val2)"
        ),
    )

    parser.add_argument(
        "--set_file",
        action="append",
        default=[],
        type=open,
        help="Specify values in a YAML file or a URL(can specify multiple) (default [])",
    )

    parser.add_argument(
        "--values",
        "-f",
        action="append",
        default=[],
        type=open,
        help="Specify values in a YAML file or a URL(can specify multiple) (default [])",
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    arguments = parse_arguments()

    helmchart = generate_helmchart(arguments)

    chart_manifest = yaml.dump(
        data=helmchart, default_flow_style=False, explicit_start=True, sort_keys=False
    )

    print(chart_manifest)


if __name__ == "__main__":
    main()
