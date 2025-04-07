# -*- coding: utf-8 -*-
"""Click commands."""
import os
import traceback
from glob import glob
from subprocess import call

import click
from flask.cli import with_appcontext

from audiorate.extensions import db
from audiorate.public.models import Model, Sample
from audiorate.utils import load_audio_samples

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

    try:
        samples_data = load_audio_samples("samples.json", convert_keys_to_int=True)
        models_data = load_audio_samples("models.json", convert_keys_to_int=True)
        print(
            f"Found {len(samples_data)} samples and {len(models_data)} models in JSON files"
        )

        if not samples_data or not models_data:
            print("No data found in JSON files. Using default data.")
            return

        for model_id, model_data in models_data.items():
            model = Model(
                id=model_id,
                name=model_data.get("name", f"Model {model_id}"),
            )
            existing = Model.query.filter_by(id=model.id).first()
            if not existing:
                db.session.merge(model)
                print(f"Model {model.id} added to the database.")
            else:
                print(f"Model {model.id} already exists in the database.")

        db.session.flush()

        for sample_id, sample_data in samples_data.items():
            ground_truth = Sample(
                id=sample_id,
                filename=sample_data.get("ground_truth", "").split("/")[-1],
                filepath=sample_data.get("ground_truth", ""),
                text=sample_data.get("text", ""),
                is_ground_truth=True,
            )
            existing = Sample.query.filter_by(id=ground_truth.id).first()
            if not existing:
                db.session.merge(ground_truth)
                print(f"Sample {ground_truth.id} added to the database.")
            else:
                print(f"Sample {ground_truth.id} already exists in the database.")

        db.session.flush()

        variant_id = len(samples_data) + 1
        for sample_id, sample_data in samples_data.items():
            for model_id_str, filepath in sample_data.get("models", {}).items():
                model_id = int(model_id_str)
                variant = Sample(
                    id=variant_id,
                    ground_truth_id=sample_id,
                    filename=filepath.split("/")[-1],
                    filepath=filepath,
                    text=sample_data.get("text", ""),
                    is_ground_truth=False,
                    model_id=model_id,
                )
                existing = Sample.query.filter_by(
                    ground_truth_id=sample_id, model_id=model_id
                ).first()
                if not existing:
                    db.session.add(variant)
                    print(f"Variant {variant.filename} added to the database.")
                    variant_id += 1
                else:
                    print(f"Variant {variant.filename} already exists in the database.")
        db.session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.session.rollback()
        traceback.print_exc()
