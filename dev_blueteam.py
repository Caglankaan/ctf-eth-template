#! /usr/bin/env python3

import os
import subprocess
from dataclasses import dataclass
from brownie import *
import eth_account
from eth_account.hdaccount import generate_mnemonic
from signal import SIGKILL
from scripts.challenge import CONFIG as _PUBLIC_CONFIG
from scripts.private.challenge import CONFIG as _PRIVATE_CONFIG

import threading
import time
import socket
import json
import argparse
from loguru import logger

from brownie.network.account import LocalAccount
from dotenv import load_dotenv
from brownie.network import gas_price, Accounts
from brownie.network.gas.strategies import LinearScalingStrategy

load_dotenv()

INTERNAL_PORT = 8555
PLAYER_PORT = 8545
PLAYER_MNEMONIC = None
ADMIN_MNEMONIC = None
RUN_MAIN_PID = None
RUN_PLAYER_PID = None
anvil_block_time = False
CHANGE_ADMIN_MNEMONIC = False

PROJECT = None

def wait_for_port(port: int, host: str = 'localhost', timeout: float = 5.0):
    """Wait until a port starts accepting TCP connections.
    Args:
        port: Port number.
        host: Host address on which the port should exist.
        timeout: In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                   'connections.'.format(port, host)) from ex
        

def accounts_from_privatekeys(owner_private_keys, player_private_keys):
    _accounts = Accounts()
    for i in range(len(owner_private_keys)):
        _accounts.add(owner_private_keys[i])
    for i in range(len(player_private_keys)):
        _accounts.add(player_private_keys[i])
    return _accounts

def accounts_from_mnemonic(mnemonic, count=1, offset=0):

    _accounts = []

    for i in range(offset, offset + count):
        w3account = eth_account.Account.from_mnemonic(
            mnemonic, passphrase='', account_path=f"m/44'/60'/0'/0/{i}"
        )

        account = LocalAccount(w3account.address, w3account, w3account.key)
        _accounts.append(account)

    return _accounts



@dataclass
class AnvilData:
    port: str
    mnemonic: str
    rpc: str
    block: str
    extra: str
    delay: bool


def anvil_run(data: AnvilData):
    global anvil_block_time
    cmd = f'anvil --accounts 10 --port {data.port} --block-base-fee-per-gas 0 --chain-id 1337'
    _args = cmd.split(' ')

    _args.append('--mnemonic')
    _args.append(data.mnemonic)

    if data.rpc != '':
        _args.append('--fork-url')
        _args.append(data.rpc)

    if data.block != '':
        _args.append('--fork-block-number')
        _args.append(data.block)

    if data.extra != '':
        _args.extend(data.extra.split(' '))
    
    if data.delay:
        _args.append('--blockTime')
        _args.append('1')
    


    process = subprocess.Popen(
        args=_args,
        stdout=subprocess.DEVNULL
    )

    return process

def ganache_run(data: AnvilData):
    global anvil_block_time
    _cmd = f'ganache-cli --chain.vmErrorsOnRPCResponse true --wallet.totalAccounts 10 --hardfork istanbul --miner.blockGasLimit 12000000 -p "{data.port}"'
    _args = _cmd.split(' ')

    _args.append('--wallet.mnemonic')
    _args.append(data.mnemonic)

    if data.rpc != '':
        _args.append('--fork.url')
        _args.append(data.rpc)

    if data.block != '':
        _args.append('--fork.blockNumber')
        _args.append(data.block)

    if data.extra != '':
        _args.extend(data.extra.split(' '))
    
    if data.delay:
        _args.append('--blockTime')
        _args.append('1')

    process = subprocess.Popen(
        args=_args,
        stdout=subprocess.DEVNULL
    )

    return process


def run_main():
    global RUN_MAIN_PID, anvil_block_time, ADMIN_MNEMONIC

    data = AnvilData(
        port=INTERNAL_PORT,
        mnemonic=ADMIN_MNEMONIC,
        rpc=_PUBLIC_CONFIG.get('RPC', ''),
        block=_PUBLIC_CONFIG.get('BLOCK_NUMBER', ''),
        extra=_PRIVATE_CONFIG.get('extra', ''),
        delay=anvil_block_time
    )

    try:
        p = anvil_run(data)
    except FileNotFoundError:
        p = ganache_run(data)

    RUN_MAIN_PID = p.pid
    
    p.wait()
    #0x4cA35d80Dd9ab86aEeF1a0EC296Fa20Ed91d066A

def run_player():
    global PLAYER_MNEMONIC, RUN_PLAYER_PID,  anvil_block_time
    player_mnemonic = _PUBLIC_CONFIG.get("MNEMONIC", '').strip()
    if player_mnemonic == '':
        player_mnemonic = generate_mnemonic(12, "english")
    
    PLAYER_MNEMONIC = player_mnemonic
    data = AnvilData(
        port=PLAYER_PORT,
        mnemonic=player_mnemonic,
        rpc=f'http://127.0.0.1:{INTERNAL_PORT}',
        block='',
        extra=_PUBLIC_CONFIG.get('extra', ''),
        delay=anvil_block_time
    )

    try:
        p = anvil_run(data)
    except FileNotFoundError:
        p = ganache_run(data)

    RUN_PLAYER_PID = p.pid
    p.wait()


STATE = {}

def deploy(_network='', player_private_keys=[], owner_private_keys=[], gas_strategy=False):
    global STATE, PROJECT, PLAYER_MNEMONIC, ADMIN_MNEMONIC
    if _network == 'goerli':
        
        network.connect(_network)
        if PROJECT is None:
            PROJECT = project.load('.')
        if gas_strategy:
            strategy = LinearScalingStrategy("6 gwei", "70 gwei", 1.1)
            gas_price(strategy)

        STATE = {}
        if player_private_keys == [] or owner_private_keys == []:
            ATTACKER_PRIVATE_KEY = os.getenv('DEFAULT_ATTACKER_PRIVATE_KEY')
            OWNER_PRIVATE_KEY = os.getenv('DEFAULT_OWNER_PRIVATE_KEY')
            
            player_private_keys = [ATTACKER_PRIVATE_KEY]
            owner_private_keys = [OWNER_PRIVATE_KEY]
        
        accounts = accounts_from_privatekeys(owner_private_keys, player_private_keys)
        deployer = accounts[0:len(owner_private_keys)]
        player = accounts[len(owner_private_keys):]

        project.run('private/challenge_blueteam', 'deploy', [STATE, deployer, player])
        project.run('challenge_blueteam', 'deploy', [STATE, deployer, player])

        def wrap(function, every):
            def wrapped_function(*args):
                function(*args)
                threading.Timer(every, wrapped_function, [*args]).start()
            return wrapped_function

        for _runnable in _PRIVATE_CONFIG.get('RUNNABLES', []) + _PUBLIC_CONFIG.get('RUNNABLES', []):
            _f, _every = _runnable
            wrap(_f, _every)(STATE, deployer, player)
    else:        
        network.connect()
        if PROJECT is None:
            PROJECT = project.load('.')

        STATE = {}
        
        deployer = accounts_from_mnemonic(ADMIN_MNEMONIC, count=10) 
        player = accounts_from_mnemonic(PLAYER_MNEMONIC, count=10) 

        project.run('private/challenge_blueteam', 'deploy', [STATE, deployer, player])
        project.run('challenge_blueteam', 'deploy', [STATE, deployer, player])

        def wrap(function, every):
            def wrapped_function(*args):
                function(*args)
                threading.Timer(every, wrapped_function, [*args]).start()
            return wrapped_function

        for _runnable in _PRIVATE_CONFIG.get('RUNNABLES', []) + _PUBLIC_CONFIG.get('RUNNABLES', []):
            _f, _every = _runnable
            wrap(_f, _every)(STATE, deployer, player)

def dump_project_deploy(is_local=True):
    global PROJECT
    obj = {}
    for key in PROJECT.keys():
        obj[key] = []
        if is_local:
            for v in PROJECT[key]:
                obj[key].append(str(v))
        else:
            #TODO: Not sure about this, can we have few contract address for same contract?
            if len(PROJECT[key]) > 0:
                obj[key].append(str(PROJECT[key][-1]))

    return obj

def attack_to_contract(is_local = True, player_private_keys=[], owner_private_keys=[]):
    global ADMIN_MNEMONIC
    
    if is_local:
        deployer = accounts_from_mnemonic(ADMIN_MNEMONIC, count=10) 
        player = accounts_from_mnemonic(PLAYER_MNEMONIC, count=10)

    else:
        if player_private_keys == [] or owner_private_keys == []:
            ATTACKER_PRIVATE_KEY = os.getenv('DEFAULT_ATTACKER_PRIVATE_KEY')
            OWNER_PRIVATE_KEY = os.getenv('DEFAULT_OWNER_PRIVATE_KEY')
            
            player_private_keys = [ATTACKER_PRIVATE_KEY]
            owner_private_keys = [OWNER_PRIVATE_KEY]

        accounts = accounts_from_privatekeys(owner_private_keys, player_private_keys)
        deployer = accounts[0:len(owner_private_keys)]
        player = accounts[len(owner_private_keys):]


    project.run('private/solve_blueteam', 'attack', [deployer, player])


def reset(is_local=True, player_private_keys=[], owner_private_keys=[]):
    global STATE, PROJECT, PLAYER_MNEMONIC, RUN_PLAYER_PID, RUN_MAIN_PID, ADMIN_MNEMONIC, CHANGE_ADMIN_MNEMONIC
    STATE = {}
    if is_local:
        chain.reset()
        #os.kill(RUN_PLAYER_PID, SIGKILL)
        #os.kill(RUN_MAIN_PID, SIGKILL)
        PLAYER_MNEMONIC = ''
        ADMIN_MNEMONIC = generate_mnemonic(12, "english") if CHANGE_ADMIN_MNEMONIC else ADMIN_MNEMONIC
        if network.is_connected():
            logger.info("disconnecting network")
            network.disconnect()
        else:
            logger.info("network is not connected")
        deploy_local(False)
        return
    else:
        if player_private_keys == [] or owner_private_keys == []:
            ATTACKER_PRIVATE_KEY = os.getenv('DEFAULT_ATTACKER_PRIVATE_KEY')
            OWNER_PRIVATE_KEY = os.getenv('DEFAULT_OWNER_PRIVATE_KEY')
            
            player_private_keys = [ATTACKER_PRIVATE_KEY]
            owner_private_keys = [OWNER_PRIVATE_KEY]
        accounts = accounts_from_privatekeys(owner_private_keys, player_private_keys)
        deployer = accounts[0:len(owner_private_keys)]
        player = accounts[len(owner_private_keys):]

    project.run('private/challenge', 'deploy', [STATE, deployer, player])
    project.run('challenge', 'deploy', [STATE, deployer, player])

    logger.debug('================================')
    logger.debug("DEPLOYMENT READY")
    logger.debug('')
    logger.debug(json.dumps(dump_project_deploy(), indent=4))
    logger.debug('')
    if is_local:
        logger.debug(f'MNEMONIC: {PLAYER_MNEMONIC}')
        logger.debug('================================')


def deploy_local(run_exploit):
    logger.info("Deploying local")
    threading.Thread(target=run_main, args=[]).start()
    wait_for_port(INTERNAL_PORT)

    threading.Thread(target=run_player, args=[]).start()
    wait_for_port(PLAYER_PORT)

    deploy()
    logger.debug('================================')
    logger.debug("DEPLOYMENT READY")
    logger.debug('')
    logger.debug(json.dumps(dump_project_deploy(), indent=4))
    logger.debug('')
    logger.debug(f'MNEMONIC: {PLAYER_MNEMONIC}')
    logger.debug('================================')

    if run_exploit:
        attack_to_contract()


def deploy_goerli(run_exploit, player_private_keys=[], owner_private_keys=[], gas_strategy=False):
    logger.info("Deploying To Goerli Test Network")

    deploy(_network='goerli', player_private_keys=player_private_keys, owner_private_keys=owner_private_keys, gas_strategy=gas_strategy)
    logger.debug('================================')
    logger.debug("DEPLOYMENT READY")
    logger.debug('')
    logger.debug(json.dumps(dump_project_deploy(is_local=False), indent=4))
    logger.debug('')

    if run_exploit:
        attack_to_contract(is_local=False, player_private_keys=player_private_keys, owner_private_keys=owner_private_keys)

def main():
    global anvil_block_time, ADMIN_MNEMONIC, CHANGE_ADMIN_MNEMONIC
    
    parser = argparse.ArgumentParser(
                    prog = 'BlueTeam CTF Platform',
                    description = 'Deploys contracts given under public/challenge, and exploit & reset them.'
            )
    parser.add_argument('--network',default='local', help='local or goerli')
    parser.add_argument('--player_private_keys', help='Add private keys.\n Usage: --private_keys KEY1,KEY2,KEY3', default='', type=str)
    parser.add_argument('--owner_private_keys', help='Add private keys.\n Usage: --private_keys KEY1,KEY2,KEY3', default='', type=str)
    parser.add_argument('--run_exploit', help='Add this flag to run exploit right after first deploy.', action='store_true')
    parser.add_argument('--gas_strategy', help='Add this flag to enable gas strategy. ', action='store_true')
    parser.add_argument('--delay_block_mine', help='Add this flag to make anvil/ganache wait 1 second on local network.', action='store_true')
    parser.add_argument('--change_admin_mnemonic', help='Add this flag to deploy same contract to different address on local network every time.', action='store_true')

    args = parser.parse_args()
    player_private_keys = [item for item in args.player_private_keys.split(',')]
    owner_private_keys = [item for item in args.owner_private_keys.split(',')]

    if args.change_admin_mnemonic:
        CHANGE_ADMIN_MNEMONIC = True
        ADMIN_MNEMONIC = generate_mnemonic(12, "english")
    else:
        ADMIN_MNEMONIC = _PRIVATE_CONFIG.get('MNEMONIC')

    anvil_block_time = args.delay_block_mine
    
    if len(args.player_private_keys) == 0 or len(args.owner_private_keys) == 0:
        ATTACKER_PRIVATE_KEY = os.getenv('DEFAULT_ATTACKER_PRIVATE_KEY')
        OWNER_PRIVATE_KEY = os.getenv('DEFAULT_OWNER_PRIVATE_KEY')
        
        player_private_keys = [ATTACKER_PRIVATE_KEY]
        owner_private_keys = [OWNER_PRIVATE_KEY]

    if args.network == 'local':
        deploy_local(args.run_exploit)
        
    elif args.network == 'goerli':
        deploy_goerli(args.run_exploit, player_private_keys=player_private_keys, 
                    owner_private_keys=owner_private_keys, gas_strategy=args.gas_strategy)
    else:
        logger.error("We are not supporting any other network than 'local' or 'goerli' currently.")
        exit(1)
        
    is_local = True if args.network == 'local' else False

    while True:
        data = input('\n\n\n\t1- exploit\n\n\n\t2- reset\n')
        
        if data == 'exploit':
            attack_to_contract(is_local=is_local, player_private_keys=player_private_keys, owner_private_keys=owner_private_keys)
        elif data == 'reset':
            reset(is_local=is_local, player_private_keys=player_private_keys, owner_private_keys=owner_private_keys)
        else:
            logger.debug("unknown")

if __name__ == '__main__':
    main()
    
