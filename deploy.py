#!/usr/bin/env python3

from zipfile import ZipFile
from os import path, walk
from tempfile import mkdtemp

from aws_cdk.core import App

from pointing_poker.aws.resources.app_stack import AppStack

dirname = path.dirname(__file__)

tmp = mkdtemp("pointing-poker-artifacts")

function_zip_path = path.join(tmp, "function.zip")


def get_all_file_paths(directory):
    return [
        path.join(root, filename)
        for root, dirs, files in walk(directory)
        for filename in files
    ]


with ZipFile(function_zip_path, "w") as func_zip:
    func_zip.write(path.join(dirname, "pointing_poker/__init__.py"))

    for file_path in get_all_file_paths(
        path.join(dirname, "venv/lib/python3.7/site-packages")
    ):
        func_zip.write(
            file_path,
            arcname=path.relpath(file_path, "venv/lib/python3.7/site-packages"),
        )

    for file_path in [
        *get_all_file_paths(path.join(dirname, "pointing_poker/services")),
        *get_all_file_paths(path.join(dirname, "pointing_poker/aws")),
    ]:
        func_zip.write(file_path)

app = App()

AppStack(app, "pointing-poker", function_zip_path, path.join(dirname, "schema.graphql"))

app.synth()
