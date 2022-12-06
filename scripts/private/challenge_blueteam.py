from brownie import *
from brownie.network.account import LocalAccount

def deploy(state, deployer, player):
    pass

#####################
# CONFIG
#####################
# --------------------------
# FLAGS:
# --------------------------
# You can specify custom flags for the "anvil" node, such as setting the default balance
# or disabling mining with `--no-mining`, etc
#
#     > These flags will affect only the deployer node instance
#
# --------------------------
# MNEMONIC
# --------------------------
# The mnemonic used to generate the deployer accounts.
#    > It MUST be specified
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
# Does allow to specify methods that will be restricted on the player node but without exposing that information.
# Refer to JSON RPC and https://book.getfoundry.sh/reference/anvil/
# Example, restrict mining: 'RESTRICTED_RPC_METHODS': ["anvil_mine", "evm_mine"]

CONFIG = {
    'FLAGS': '', # ex: --balance 10, ...
    'MNEMONIC': 'salad wrong armed concert evolve clock alter pledge run scout person essay', # ex: salad wrong armed concert evolve clock alter pledge run scout person essay
    'RUNNABLES': [], # ex: [(function, 2), (more_function, 10)] ### (function, seconds)
    'RESTRICTED_RPC_METHODS': ['anvil_*', 'evm_*'] # Disables mining/sleep without exposing that information to the player
}