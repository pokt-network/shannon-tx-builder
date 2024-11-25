# Shannon Tx Builder <!-- omit in toc -->

Shannon tx builder is a UI that uses that simplifies some of the common
`poktrolld` CLI operations for new users.

This repository is a very active WIP and should be treated as a HACK for now.

- [TestNet](#testnet)
  - [Beta TestNet](#beta-testnet)
  - [ALpha TestNet](#alpha-testnet)
- [LocalNet](#localnet)
- [Developing this application](#developing-this-application)
  - [Environment Setup (One Time)](#environment-setup-one-time)
  - [Environment Usage (Every Time)](#environment-usage-every-time)

## TestNet

Where can I find the secrets for TestNet to deplo this app?

### Beta TestNet

You can find the secrets for Beta TestNet in Grove's Notion [here](https://www.notion.so/buildwithgrove/Shannon-Beta-TestNet-Genesis-Configs-144a36edfff6802597a1fa4c39ef3fcb?pvs=4).

### ALpha TestNet

TODO

## LocalNet

Make a copy of the `.env.example` file and update the values as needed.

```bash
cp .env.example .env
```

## Developing this application

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
