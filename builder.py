import sys
import argparse
import re
from pathlib import Path

SSL_CERTIFICATE_FILENAME = "fullchain.pem"
SSL_CERTIFICATE_KEY_FILENAME = "privkey.pem"

NGINX_PATH = Path("/etc/nginx")
BASIC_CONF_PATH = Path(__file__).parent / "basic.conf"
SSL_CONF_PATH = Path(__file__).parent / "ssl.conf"


class NginxBuilderError(Exception):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_name")
    parser.add_argument("proxy_pass")
    parser.add_argument(
        "-ssl",
        help=f"Absolute Path to directory where {SSL_CERTIFICATE_FILENAME!r} and {SSL_CERTIFICATE_KEY_FILENAME!r} files are stored",
    )
    parser.add_argument(
        "--copy-and-link",
        action="store_true",
        default=False,
        help="Copies created config to '/etc/nginx/sites-available' and creates symbolic link (ln -s) between 'sites-available' and 'sites-enabled' config file",
    )

    args = parser.parse_args()

    sys.stdout.write(f"{'NGINX=REVERSE=PROXY=CONF=BUILDER':=^79}\n")

    base_config_path = BASIC_CONF_PATH

    replace_table = {
        "#SERVER_NAME": args.server_name,
        "#PROXY_PASS": args.proxy_pass,
    }

    if args.ssl:
        sys.stdout.write(f"{'Using SSL config':=^79}\n")

        base_config_path = SSL_CONF_PATH
        ssl_path = Path(args.ssl)
        cert = ssl_path / SSL_CERTIFICATE_FILENAME
        cert_key = ssl_path / SSL_CERTIFICATE_KEY_FILENAME

        if any_not_found := tuple(
            filter(lambda path: not path.exists(), (ssl_path, cert, cert_key))
        ):
            raise FileNotFoundError(f"SSL files {any_not_found!r} not found.")

        replace_table.update(
            {
                "#SSL_CERTIFICATE": str(ssl_path / SSL_CERTIFICATE_FILENAME),
                "#SSL_CERTIFICATE_KEY": str(ssl_path / SSL_CERTIFICATE_KEY_FILENAME),
            }
        )

    sys.stdout.write(f"{'Building conf file for ' + args.server_name :=^79}\n")

    with open(base_config_path, "r") as f:
        base = f.read()

    for key, value in replace_table.items():
        base = re.sub(rf"{key}\b", value, base)

    result_path = Path(__file__).parent / f"{args.server_name}.conf"

    with open(result_path, "w") as f:
        f.write(base)

    sys.stdout.write(f"{'Success! Saved as ' + result_path.name :=^79}\n")

    if args.copy_and_link:
        import subprocess

        sites_available_path = NGINX_PATH / "sites-available" / result_path.name
        sites_enabled_path = NGINX_PATH / "sites-enabled" / result_path.name

        cp_cmd = ("cp", str(result_path), str(sites_available_path))
        r = subprocess.run(cp_cmd, capture_output=True)

        if r.returncode != 0:
            raise NginxBuilderError(
                f"Error while running {cp_cmd!r}!\n\tstderr: {r.stderr}"
            )

        ln_cmd = ("ln", "-s", str(sites_available_path), str(sites_enabled_path))
        r = subprocess.run(ln_cmd, capture_output=True)

        if r.returncode != 0:
            raise NginxBuilderError(
                f"Error while running {ln_cmd!r}!\n\tstderr: {r.stderr}"
            )

        sys.stdout.write(f"{'Copy and link - Success!':=^79}\n")


if __name__ == "__main__":
    main()
