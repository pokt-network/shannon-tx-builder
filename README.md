# Shannon Tx Builder <!-- omit in toc -->

- [LocalNet](#localnet)
- [Development](#development)
  - [Environment Setup (One Time)](#environment-setup-one-time)
  - [Environment Usage (Every Time)](#environment-usage-every-time)

## LocalNet

Make a copy of the `.env.example` file and update the values as needed.

```bash
cp .env.example .env
```

## Development

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
