import json
from pathlib import Path
from string import Template

import boto3
from fabric.api import local, settings
from fabric.contrib.console import confirm
from fabric.utils import abort


__all__ = ["update_environment_variables"]


def get_aws_credentials(session: boto3.session.Session) -> tuple[str, str]:
    credentials = session.get_credentials()
    return credentials.access_key, credentials.secret_key


def get_aws_secret(session: boto3.session.Session, secret_name: str) -> dict:
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def read_env_template(input_template_path: Path | str) -> Template:
    with open(input_template_path) as input_template_file:
        return Template(input_template_file.read())


def write_env_file_with_substitutions(output_file_path, env_template: Template, substitutions: dict):
    with open(output_file_path, "w") as new_env_fp:
        new_env_fp.write(env_template.substitute(substitutions))


def get_user_confirmation(existing_file: Path, new_file: Path) -> bool:
    with settings(warn_only=True):
        local(f"diff -N {existing_file} {new_file}")
    return confirm("Are you happy to overwrite the env file with these changes?")


def update_environment_variables(
    template_file_path: Path | str,
    secrets_manager_secret: str,
    secrets_manager_region: str,
    aws_profile_name: str = "default",
    extra_subs: dict | None = None,
    prioritise_extra_subs: bool = False,
    output_file_path: Path | str | None = None,
    with_confirm: bool = True,
) -> None:
    """Generate a .env file by merging an env template file with secrets stored in Secrets Manager"""

    session = boto3.Session(profile_name=aws_profile_name, region_name=secrets_manager_region)
    secret = get_aws_secret(session, secrets_manager_secret)

    template = read_env_template(template_file_path)

    # The dict union operator will prioritise any duplicate keys in the RHS dict
    substitutions = (secret | extra_subs) if prioritise_extra_subs else (extra_subs | secret)

    if output_file_path is None:
        # put in the same folder as the original env template if output is unspecified
        output_file_path = Path(template_file_path).parent / ".env"
    elif isinstance(output_file_path, str):
        output_file_path = Path(output_file_path)

    temp_output_file_path = output_file_path.parent / ".env.new"

    write_env_file_with_substitutions(temp_output_file_path, template, substitutions)

    if with_confirm and not get_user_confirmation(output_file_path, temp_output_file_path):
        local(f"rm {temp_output_file_path}")
        abort("No changes were made to the existing environment file")
    local(f"rm -f {output_file_path}")
    local(f"mv {temp_output_file_path} {output_file_path}")
