#!/usr/bin/env python3

from zipfile import ZipFile
from os import path
from tempfile import mkdtemp

from aws_cdk.core import App

from pointing_poker.aws.resources.app_stack import AppStack

dirname = path.dirname(__file__)

tmp = mkdtemp("pointing-poker-artifacts")

function_zip_path = path.join(tmp, "function.zip")

with ZipFile(function_zip_path, "w") as func_zip:
    func_zip.write(path.join(dirname, "venv/lib/python3.7/site-packages"))
    func_zip.write(path.join(dirname, "pointing_poker/aws/controllers/sessions.py"))

app = App()

AppStack(app, "pointing-poker", function_zip_path, path.join(dirname, "schema.graphql"))

app.synth()
