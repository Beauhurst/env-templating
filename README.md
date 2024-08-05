# Environment Templating

Tool for using Secrets Manger to substitute variables into `.env` template files.

## Installation

### Prerequisites
- AWS CLI - installed and configured
- Python 3.10+ environment

Run the following:
```shell
pip install git+https://github.com/Beauhurst/env-templating.git@main
```
Or add `git+https://github.com/Beauhurst/env-templating.git@main` to your `requirements.txt` file.

(If you want a specific release, replace `main` with the appropriate tag)

## Usage

### On Secrets Manager

Store your secrets in AWS Secrets Manager as JSON key/value pairs.

See the AWS docs for instructions on how to do this https://docs.aws.amazon.com/secretsmanager/latest/userguide/create_secret.html

### In your repository

Create a file representing the template for your environment file (e.g. `.env.template`). 
Any values that you want to substitute should be surrounded by `${}`.
Any non-secret values that are the same across environments can be written in plain text.

An example of a template file:
```
MY_SECRET_KEY=${MY_SECRET_KEY}
ANOTHER_SECRET_KEY=${ANOTHER_SECRET_KEY}
SHARED_AND_NOT_SECRET=1234
```

In your script:

```python
from pathlib import Path

from env_templating.templating import update_environment_variables

update_environment_variables(
    Path("path/to/your/.env.template"),
    "name/of/your/secret",
    "name/of/aws/region"
)
```

Supported arguments:

* `template_file_path: Path | str` (required) - The path to your env template file
* `secrets_manager_secret: str` (required) - The name of the secret you have stored in AWS Secrets Manager
* `secrets_manager_region: str` (required) - The name of the AWS region the secret is stored in (e.g. `eu-west-2`)
* `extra_substitutions: dict | None = None` - A dictionary of key/value pairs to substitute into your template in addition to those in your secret
* `prioritise_extra_substitutions: bool = False` - Whether extra substitutions take priority over those in the secret where there are duplicate keys 
* `output_file_path: Path | str | None = None` - Where to output the final env file (if not set this library will put this in the same folder as your template file)
* `with_confirm: bool = True` - Whether to show a diff and get confirmation from the user before replacing the existing file


### AWS Permissions

The user running the substitution script must have appropriate read permissions for the secret that contains the substitutions.

A minimal example:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetResourcePolicy",
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": [
              "arn:aws:secretsmanager:*:<YOUR-ACCOUNT-ID>:secret:<NAME/OF/YOUR/SECRET>-??????"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetRandomPassword",
                "secretsmanager:ListSecrets"
            ],
            "Resource": "*"
        }
    ]
}
```
