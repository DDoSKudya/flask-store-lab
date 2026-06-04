import os


def get_env_var(var_name: str) -> str:
    """
    Retrieve a required environment variable by name.

    Enforces presence of the variable and converts missing keys into a user-friendly
    error.

    Args:
        var_name:
            Name of the environment variable to look up.

    Returns:
        The value of the requested environment variable.

    Raises:
        ValueError:
            If the environment variable is not set in the current process.
    """
    try:
        return os.environ[var_name]
    except KeyError as exc:
        raise ValueError(f"{var_name} is not set") from exc
