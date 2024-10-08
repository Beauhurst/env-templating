import sys
from pathlib import Path
from string import Template

from .aws import get_aws_secret
from .util import confirm, run


__all__ = ["update_environment_variables"]


def _read_env_template(input_template_path: Path | str) -> Template:
    """Open a text file and convert it to a Template object"""
    with open(input_template_path) as input_template_file:
        return Template(input_template_file.read())


def _write_env_file_with_substitutions(output_file_path: Path, env_template: Template, substitutions: dict):
    """Make substitutions into a Template object and write resulting string to file"""
    with open(output_file_path, "w") as new_env_fp:
        new_env_fp.write(env_template.substitute(substitutions))


def _get_user_confirmation(existing_file: Path, new_file: Path) -> bool:
    """Present a diff comparing the old file to the new and prompt user for confirmation"""
    run(f"diff -N {existing_file} {new_file}", warn=True)
    return confirm("Are you happy to overwrite the env file with these changes?")


def update_environment_variables(
    template_file_path: Path | str,
    secrets_manager_secret: str,
    secrets_manager_region: str,
    extra_substitutions: dict | None = None,
    prioritise_extra_substitutions: bool = False,
    output_file_path: Path | str | None = None,
    with_confirm: bool = True,
) -> None:
    """Generate a .env file by merging an env template file with secrets stored in Secrets Manager"""

    if not extra_substitutions:
        if prioritise_extra_substitutions:
            raise ValueError("`extra_substitutions` must be set if using `prioritise_extra_substitutions`")
        extra_substitutions = {}

    secret = get_aws_secret(secrets_manager_secret, secrets_manager_region)

    template = _read_env_template(template_file_path)

    # The dict union operator will prioritise any duplicate keys in the RHS dict
    substitutions = (secret | extra_substitutions) if prioritise_extra_substitutions else (extra_substitutions | secret)

    if output_file_path is None:
        # put in the same folder as the original env template if output is unspecified
        output_file_path = Path(template_file_path).parent / ".env"
    elif isinstance(output_file_path, str):
        output_file_path = Path(output_file_path)

    temp_output_file_path = output_file_path.parent / ".env.new"

    _write_env_file_with_substitutions(temp_output_file_path, template, substitutions)

    if with_confirm and not _get_user_confirmation(output_file_path, temp_output_file_path):
        run(f"rm {temp_output_file_path}")
        print("No changes were made to the existing environment file")
        return
    run(f"rm -f {output_file_path}")
    run(f"mv {temp_output_file_path} {output_file_path}")
