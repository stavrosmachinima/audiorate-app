# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call

import click
from flask.cli import with_appcontext

from audiorate.extensions import db
from audiorate.public.models import Model, Sample

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
@click.option(
    "-c/-C",
    "--coverage/--no-coverage",
    default=True,
    is_flag=True,
    help="Show coverage report",
)
@click.option(
    "-k",
    "--filter",
    default=None,
    help="Filter tests by keyword expressions",
)
def test(coverage, filter):
    """Run the tests."""
    import pytest

    args = [TEST_PATH, "--verbose"]
    if coverage:
        args.append("--cov=audiorate")
    if filter:
        args.extend(["-k", filter])
    rv = pytest.main(args=args)
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=True,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
@click.option(
    "-c",
    "--check",
    default=False,
    is_flag=True,
    help="Don't make any changes to files, just confirm they are formatted correctly",
)
def lint(fix_imports, check):
    """Lint and check code style with black, flake8 and isort."""
    skip = ["node_modules", "requirements", "migrations"]
    root_files = glob("*.py")
    root_directories = [
        name for name in next(os.walk("."))[1] if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip
    ]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo(f"{description}: {' '.join(command_line)}")
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    isort_args = []
    black_args = []
    if check:
        isort_args.append("--check")
        black_args.append("--check")
    if fix_imports:
        execute_tool("Fixing import order", "isort", *isort_args)
    execute_tool("Formatting style", "black", *black_args)
    execute_tool("Checking code style", "flake8")


@click.command()
@with_appcontext
def seed():
    """Seed the database with initial data."""
    print("Seeding database...")

    samples = [
        Sample(
            id=1,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
        Sample(
            id=2,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
        Sample(
            id=3,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
        Sample(
            id=4,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
        Sample(
            id=5,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
        Sample(
            id=6,
            audio_file="22050_lasagna.wav",
            transcript="So... this cat loves lasagna so much that he eats all of the lasagna in his house. Okay, apparently it's not the cat's house or his lasagna. Oh good! The man who owns the lasagna is furious!",
        ),
    ]
    for sample in samples:
        existing = Sample.query.filter_by(id=sample.id).first()
        if not existing:
            db.session.merge(sample)

    models = [
        Model(id=1, name="ForwardTacotron"),
        Model(id=2, name="FastPitch"),
        Model(id=3, name="FastSpeech 2"),
    ]
    for model in models:
        existing = Model.query.filter_by(name=model.name).first()
        if not existing:
            db.session.merge(model)

    db.session.commit()
    print("Database seeded.")
