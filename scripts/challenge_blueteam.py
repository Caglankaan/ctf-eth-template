from brownie import *

def deploy(STATE, deployer, attacker):
    deployer = deployer[0]
    attacker = attacker[0]
    print("Deploying/reseting tokens.\n\n")
    halbornNFT = HalbornNFT.deploy({'from': deployer})
    ercToken = ApeCoin.deploy({'from': deployer})
    
    ercToken.mint(deployer, 500)
    ercToken.mint(attacker, 500)
    
    halbornNFT.safeMint(deployer, 0)
        
    marketPlaceToken = NFTMarketplace.deploy(deployer, ercToken, halbornNFT, {'from': deployer})

    ercToken.approve(marketPlaceToken, 500, {'from': deployer})
    ercToken.approve(marketPlaceToken, 500, {'from': attacker})

    halbornNFT.approve(marketPlaceToken, 0, {'from': deployer})
    

# This function should return a tuple of 2 values
# - First value is a boolean, if the challenge was solved or not
# - Second value is a message to display on the CTF platform

# You can use the "state" to retrieve global state set by any other
# function including runnables
def solved(state, deployer, player):
    return False, "Need more coins!"
    #if Test[-1].balance() > 0:
    #    return True, "Solved!"
    #else:
    #    return False, "Need more coins!"

#####################
# CONFIG
#####################
# --------------------------
# RPC & BLOCK_NUMBER:
# --------------------------
# It is used to fork from a testnet/mainnet RPC url from an specific BLOCK_NUMBER
#
# --------------------------
# FLAGS:
# --------------------------
# You can specify custom flags for the "anvil" node, such as setting the default balance
# or disabling mining with `--no-mining`, etc
#
#     > These flags will affect only the player node instance
#
# --------------------------
# MNEMONIC
# --------------------------
# The mnemonic used to generate the player accounts, if not specified it is randomly generated
#
# --------------------------
# RUNNABLES:
# --------------------------
# You can create custom functions that can be executed every x seconds,
# they take 3 arguments, the state, deployer and player accounts.
#
#        def check_for_low_balance(state, deployer, player):
#            state['low_balance'] = False
#            if player[0].balance < web3.toWei(1, 'ether'):
#                state['low_balance'] = True
# On the CONFIG file you can add runnables by storing a tuple of (function, seconds):
#      'RUNNABLES': [(check_for_low_balance, 10)],
#
# This will add the check_for_low_balance function to be executed every 10 seconds
#
# More Examples:
# For example when mining is disabled you could check for pending
# mempool txs and act on it modifying the "state" and reporting that the challenge
# is solved under "solved"
#
# --------------------------
# RESTRICTED_RPC_METHODS
# --------------------------
#
# Does allow to specify methods that will be restricted on the player node.
# Refer to JSON RPC and https://book.getfoundry.sh/reference/anvil/
# Example, restrict mining: 'RESTRICTED_RPC_METHODS': ["anvil_mine", "evm_mine"]

CONFIG = {
    "RPC": '', # ex: https://rpc.ankr.com/eth
    "BLOCK_NUMBER": '', # 1234567
    'FLAGS': '', # ex: --balance 10, --no-mining, ...
    'MNEMONIC': '', # ex: test test test test test test test test test test test junk
    'RUNNABLES': [], # ex: [(function, 2), (more_function, 10)] ### (function, seconds)
    'RESTRICTED_RPC_METHODS': ['anvil_*', 'evm_*'] # Disables mining/sleep
}