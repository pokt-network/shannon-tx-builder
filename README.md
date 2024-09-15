## Getting Started

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

Tab 1: I want to deploy a gateqat

- Click here to generate an address
- Click here to fund it
- Prepare a staking config
- Stake your node
- Prepare an operation config

Tab2: I want to deploy a supplier

- Click here to generate an address
- Click here to fund it
- Prepare a staking config
- Prepare an operation config

Technical details:

- Can I embed poktroll in the streamlit?
  - Easy usage
- Can I embed the private key for the faucet in stremlit?
  - Easy funding
- Need an RPC endpoint to make this easy
- What's the easiest way to modify yaml files via configs?
- Can I have multiple tabs?
- How do I make it interactive for the user?
