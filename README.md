# Shannon Tx Builder <!-- omit in toc -->

Shannon tx builder is a UI that uses that simplifies some of the common
`poktrolld` CLI operations for new users.

This repository is a very active WIP and should be treated as a HACK for now.

- [Secrets](#secrets)
- [Development Quickstart](#development-quickstart)
  - [Environment Setup (One Time)](#environment-setup-one-time)
  - [Environment Usage (Every Time)](#environment-usage-every-time)
- [Local Usage](#local-usage)
- [LocalNet](#localnet)
  - [ALpha TestNet](#alpha-testnet)
  - [Beta TestNet](#beta-testnet)

## Secrets

If you are a member of the Grove team, you can find the secrets in 1Password [here](https://start.1password.com/open/i?a=4PU7ZENUCRCRTNSQWQ7PWCV2RM&v=6vfwx26ff2yczyywrzm32bwt2e&i=ubqe76vwcrhlgnievfu64klcpq&h=buildwithgrove.1password.com).

Find a file by the name of `Shannon Tx Builder Secrets` and copy its contents into `.streamlit/secrets.toml`.

## Development Quickstart

### Environment Setup (One Time)

```bash
make env_create
$(make env_source)
make pip_install
```

### Environment Usage (Every Time)

```bash
$(make env_source) # If new dependencies were added
make pip_freeze
```

## Local Usage

## LocalNet

```bash
make run_localnet
```

### ALpha TestNet

```bash
make run_alpha_testnet
```

### Beta TestNet

```bash
make run_beta_testnet
```
