# gitea_env_extractor

extracts a blank .env to use in `docker-compose.yml` from the gitea config cheat sheet

## Usage

1. copy html from the inner section of <https://docs.gitea.com/next/administration/config-cheat-sheet>
1. run `extract_env.py`
1. fix any errors by hand

or just use the provided `gitea.env` as is
