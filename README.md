# Halborn ETH CTF Template

## Requirements

- Brownie
- Docker (optional)

# Red Team CTF

## Description


To create a new challenge use this repository as a base:

- It is a standard brownie project folder with `/contracts` and a default `brownie-config.yaml` config for you to modify.
- The `scripts/private` folder can be used to store solutions or walkthroughs.
- The challenge details that will be displayed on the ctf page can be found under `challenge.yml` and should be edited acordingly.
- If the challenge does make use of real chain data, aka forking, you can define the information under the CONFIG variable of the `scripts/challenge.py` file.

There are 2 `challenge.py` files, used to deploy and manage the challenge, one under `scripts` and the other under `scripts/private`. The former, called PUBLIC will be exposed to the player as part of the CTF challenge files. It allows to set the configuration and settings for the player node instance, the one the player will connect to.

> If you need private deployments or perform private runnable actions you can modify the `scripts/private/challenge.py` file instead. This file will be hidden from the player and never exposed on the CTF platform.

All functions, including runnables, defined under `challenge.py` take 3 arguments by default:

```
- deployer: Those accounts should be used to deploy the challenge, you can think of them as being
            the "admin" accounts. They will be restricted by default, even if
            the player is capable of obtaining the private key, sending
            any transaction from those addresses will cause an exception on the backend.

            You MUST set a MNEMONIC under scripts/private/challenge.py (CONFIG["MNEMONIC"])
            default: 10 accounts

- player:   Those accounts are randomly generated unless specified under
            scripts/challenge.py (CONFIG) by setting the MNEMONIC.
            default: 10 accounts

- state:    This is a dictionary container that allows you to store anything you would require
            in any other function, such as runnables or "solved". For example, you could be using
            the state variable under a runnable to check for certain condition to be meet. Once this
            condition in met you could set an entry under the state variable to some value and check
            it under the "solved" function to display a different message, or solve the challenge.
```

> You can set the default balance by changing the FLAGS of the CONFIG either on the PUBLIC or PRIVATE config, depending if you want different balance on the deployer accounts or the player accounts.

## Developing

- Create/copy your contracts under `contracts` and develop your deployment scripts

- Execute the following command under a separated terminal to start the development environment. This environment will run the deployment scripts and take all the configurations as the real platform would doo. Runnables are also supported and executed:

```
./dev.py
```

Once you see the following without any error, the dev environment is ready to play and the deployment was successful.

```
================================
DEPLOYMENT READY

{
    "Test": [
        "0xaE5971a1b501755d2c830f59609b90CD6aa08eD7"
    ]
}

MNEMONIC: away despair village call pipe cement banner motor tomato know pitch crime
================================
```

> Notice that the reported addresses are the ones the player will be given on the CTFd platform and the mnemonic is the player mnemonic.

- Connect to `http://127.0.0.1:8545` or run `brownie console` on the same folder. (Use the player mnemonic if your RPC client does not fetch the accounts)
- On the terminal that the `dev.py` script was executed you can check if the challenge was solved by pressing the return key: 
    - The dev environment will take care of sending the correct state, deployment and player accounts.

```
================================
Check solved? <RETURN>

Running 'scripts/challenge.py::solved'...
[
    false,
    "Need more coins!"
]
Check solved?
```

- Modify the `challenge.yml`

# Check container

Once the challenge is fully coded it is a good idea to make sure the docker image does build and deploys the challenge successfully:

```
cd public
docker build . -t challenge-dev
docker run -p 8545:80 --rm challenge-dev
```

If no errors are shown the challenge is ready!

- Try to run the solve script against the `http://127.0.0.1:8545` instance created by the previous docker run.
- Get details with `curl http://127.0.0.1:8545/details`

# Tricks

You can disable mining by calling this method:

```
web3.provider.make_request("evm_setAutomine", [False])
```


# Blue Team CTF

## Description

To create a new challenge use this repository as a base:

- It is a standard brownie project folder with `/contracts` and a default `brownie-config.yaml` config for you to modify.
- The `scripts/private` folder is used to store the attack function for the manager to run exploit.

There are 2 `challenge.py` files, used to deploy and manage the challenge, one under `scripts` and the other under `scripts/private`. The former, called PUBLIC will be exposed to the player as part of the CTF challenge files. It allows to set the configuration and settings for the player node instance, the one the player will connect to.

> If you need private deployments or perform private runnable actions you can modify the `scripts/private/challenge.py` file instead. This file will be hidden from the player and never exposed on the CTF platform.

All functions, including runnables, defined under `challenge.py` take 3 arguments by default:

```
- deployer: Those accounts should be used to deploy the challenge, you can think of them as being
            the "admin" accounts. They will be restricted by default, even if
            the player is capable of obtaining the private key, sending
            any transaction from those addresses will cause an exception on the backend.

            If you are planning to run CTF in a local network:
                You MUST set a MNEMONIC under scripts/private/challenge.py (CONFIG["MNEMONIC"])
                default: 10 accounts
            If you are planning to run CTF in a test network:
                You either MUST set a private key for an owner in the `.env` file or you MUST give
                a private key array when running the program for more admin accounts.

- player:   If you are planning to run CTF in a local network:
                Those accounts are randomly generated unless specified under
                scripts/challenge.py (CONFIG) by setting the MNEMONIC.
                default: 10 accounts
            If you are planning to run CTF in a test network:
                You either MUST set a private key for an attacker in the `.env` file or you MUST 
                give a private key array when running the program for more attacker accounts.
                
 
- state:    This is a dictionary container that allows you to store anything you would require
            in any other function, such as runnables or "solved". For example, you could be using
            the state variable under a runnable to check for certain condition to be meet. Once this
            condition in met you could set an entry under the state variable to some value and check
            it under the "solved" function to display a different message, or solve the challenge.
```

> You can set the default balance by changing the FLAGS of the CONFIG either on the PUBLIC or PRIVATE config, depending if you want different balance on the deployer accounts or the player accounts.

## Developing

- Create/copy your contracts under `contracts` and develop your deployment scripts

There are few options that can be set when executing the platform.

```
./dev_blueteam.py --help
usage: BlueTeam CTF Platform [-h] [--network NETWORK] [--player_private_keys PLAYER_PRIVATE_KEYS] [--owner_private_keys OWNER_PRIVATE_KEYS] [--run_exploit] [--gas_strategy]
                             [--delay_block_mine] [--change_admin_mnemonic]

Deploys contracts given under public/challenge, and exploit & reset them.

options:
  -h, --help            show this help message and exit
  --network NETWORK     local or goerli
  --player_private_keys PLAYER_PRIVATE_KEYS
                        Add private keys. Usage: --private_keys KEY1,KEY2,KEY3
  --owner_private_keys OWNER_PRIVATE_KEYS
                        Add private keys. Usage: --private_keys KEY1,KEY2,KEY3
  --run_exploit         Add this flag to run exploit right after first deploy.
  --gas_strategy        Add this flag to enable gas strategy.
  --delay_block_mine    Add this flag to make anvil/ganache wait 1 second on local network.
  --change_admin_mnemonic
                        Add this flag to deploy same contract to different address on local network every time.
```
 - In default, all of those flags are False/empty, so if you start the platform without any flag it will setup normal local network.

```
./dev_blueteam.py 
```

Once you see the following without any error, the dev environment is ready to play and the deployment was successful.

```
2022-12-07 11:32:10.634 | DEBUG    | __main__:deploy_local:348 - ================================
2022-12-07 11:32:10.634 | DEBUG    | __main__:deploy_local:349 - DEPLOYMENT READY
2022-12-07 11:32:10.634 | DEBUG    | __main__:deploy_local:350 - 
2022-12-07 11:32:10.635 | DEBUG    | __main__:deploy_local:351 - {
    "NFTMarketplace": [
        "0x4cA35d80Dd9ab86aEeF1a0EC296Fa20Ed91d066A"
    ],
    "HalbornNFT": [
        "0x0cB8C2Fe5f94B3b9a569Df43a9155AC008c9884b"
    ],
    "ApeCoin": [
        "0xAD6d3449eDfDe7192EaA3e4803FfC79532136F11"
    ],
    "HalbornToken": [],
    "Test": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/ERC721": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/ERC20": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Address": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Strings": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Counters": []
}
2022-12-07 11:32:10.635 | DEBUG    | __main__:deploy_local:352 - 
2022-12-07 11:32:10.635 | DEBUG    | __main__:deploy_local:353 - MNEMONIC: letter until that feel require sketch kiwi hello day pretty toilet river
2022-12-07 11:32:10.637 | DEBUG    | __main__:deploy_local:354 - ================================



        1- exploit


        2- reset

```
After that step program is expecting us to `reset` or `exploit` the contracts. After setting up the `forta-agent` environment the manager will be able to exploit contract with one click.

```
2022-12-07 11:36:55.156 | DEBUG    | __main__:deploy_local:354 - ================================



        1- exploit


        2- reset
exploit

Running 'scripts/private/solve_blueteam.py::attack'...
players initial balance:  500
Transaction sent: 0xbf581cf99a0a0c5cc2427a7b1f00a3ea7b348d1a18bdfcbb18e8f344d7a59de2
  Gas price: 0.0 gwei   Gas limit: 30000000   Nonce: 1
  NFTMarketplace.postBuyOrder confirmed   Block: 25   Gas used: 169113 (0.56%)

decreaseBuyOrder player:  0x9A9E801a5B2d1F7393b05914E6C9FCfaB46a7F00  decreaseAmount:  399
Transaction sent: 0x73c3884c1ee8a9d6c45d1d5c68df0a19c0301a2f90054d1fe39da8d02b390a1c
  Gas price: 10.0 gwei   Gas limit: 30000000   Nonce: 2
Transaction sent: 0x2e2a63a56a2cf44e05b61d61d5d9a5700aff42f4e8b10a9d56bb499e6f6a22f3
  Gas price: 0.0 gwei   Gas limit: 30000000   Nonce: 8
  NFTMarketplace.decreaseBuyOrder confirmed   Block: 26   Gas used: 50993 (0.17%)

  NFTMarketplace.sellToOrderId confirmed   Block: 26   Gas used: 117032 (0.39%)

players final balance:  499
                assert finalBalanceOfplayer == initialBalanceOfplayer - 1 passed!
                assert nftOwner == self.player.address passed!
frontRunningVulnerability exploited successfully! 
```

Meanwhile `forta-agent` will be able to catch issue 

```
1 findings for transaction 0x2e2a63a56a2cf44e05b61d61d5d9a5700aff42f4e8b10a9d56bb499e6f6a22f3 {
  "name": "SelltoOrderId frontrunning",
  "description": "Malicious actor decreased buy order with frontrunning!",
  "alertId": "FORTA-1",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Exploit",
  "metadata": {},
  "addresses": [],
  "labels": []
}
```

After that step, it is also possible to `reset` the whole environment again with one click, and the manager will be able to reset and re-exploit the environment over and over again. If worked contract should be deployed on the test network steps are pretty much the same, we only have to add a few flags when running the program.
```
./dev_blueteam.py --network goerli --gas_strategy True --player_private_keys ****** --owner_private_keys ******
```
And if given accounts has enough ethers, everything will be succeeded and contracts will be deployed on goerli network.
```
2022-12-07 11:44:13.012 | DEBUG    | __main__:deploy_goerli:364 - ================================
2022-12-07 11:44:13.013 | DEBUG    | __main__:deploy_goerli:365 - DEPLOYMENT READY
2022-12-07 11:44:13.013 | DEBUG    | __main__:deploy_goerli:366 - 
2022-12-07 11:44:13.014 | DEBUG    | __main__:deploy_goerli:367 - {
    "NFTMarketplace": [
        "0xb1a8857e295cFEFEDE2659980A444a35C2C215CF"
    ],
    "HalbornNFT": [
        "0xBe69491Ed9713620f32fd170Dd1dBCd4D789Fa55"
    ],
    "ApeCoin": [
        "0xa950Ed9325Cd4f55187EE748D97d200466c2b32a"
    ],
    "HalbornToken": [],
    "Test": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/ERC721": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/ERC20": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Address": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Strings": [],
    "OpenZeppelin/openzeppelin-contracts@4.5.0/Counters": []
}
2022-12-07 11:44:13.014 | DEBUG    | __main__:deploy_goerli:368 - 



        1- exploit


        2- reset
exploit

Running 'scripts/private/solve_blueteam.py::attack'...
players initial balance:  500
Transaction sent: 0x00092d33933446bba7319ae793f5103a83a48ca3b25c2ca668b7383ede053197
  Gas price: 6.0 gwei   Gas limit: 191513   Nonce: 42
  NFTMarketplace.postBuyOrder confirmed   Block: 8090711   Gas used: 169113 (88.30%)

decreaseBuyOrder player:  0x255ba4faa1a90DF35f2eE597265c7EC22D1221cB  decreaseAmount:  399
Transaction sent: 0xe628eadd81731af4b407975b53f5468d32a9265c84a1ec3f9f7b1c2026e4facf
  Gas price: 6.0 gwei   Gas limit: 150066   Nonce: 159
Transaction sent: 0x1e1923ccf92ea99f2feaf0aeb18abb31f3ff060b1e16085124743148ab522e05
  Gas price: 10.0 gwei   Gas limit: 61581   Nonce: 43
  NFTMarketplace.decreaseBuyOrder confirmed   Block: 8090712   Gas used: 50993 (82.81%)

  NFTMarketplace.sellToOrderId confirmed   Block: 8090712   Gas used: 117032 (77.99%)

players final balance:  499
                assert finalBalanceOfplayer == initialBalanceOfplayer - 1 passed!
                assert nftOwner == self.player.address passed!
frontRunningVulnerability exploited successfuly! 
```

And again the `forta-agent` will be able to catch vulnerability
```
1 findings for transaction 0xe628eadd81731af4b407975b53f5468d32a9265c84a1ec3f9f7b1c2026e4facf {
  "name": "SelltoOrderId frontrunning",
  "description": "Malicious actor decreased buy order with frontrunning!",
  "alertId": "FORTA-1",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Exploit",
  "metadata": {},
  "addresses": [],
  "labels": []
}
```

[Goerli network contract link](https://goerli.etherscan.io/address/0xb1a8857e295cFEFEDE2659980A444a35C2C215CF)