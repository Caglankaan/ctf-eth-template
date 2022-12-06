
import {
    Finding,
    HandleTransaction,
    TransactionEvent,
    FindingSeverity,
    FindingType,
  } from "forta-agent";
  
  export const BuyOrderDecreasedEvent = 
  "event BuyOrderDecreased(uint256 indexed orderId, uint256 indexed decreaseAmount);"
  export const BuyOrderFullFilledEvent = "event BuyOrderFulfilled(uint256 indexed orderId);"
  export const BuyOrderListedEvent = 
  "event BuyOrderListed(address indexed owner,uint256 indexed orderId,uint256 indexed nftId,uint256 erc20Amount);"
  //Change nft marketplace address
  export const NFT_MARKETPLACE_ADDRESS = "0x29288A222d0DAa1d9891171c45Ed4a6f7D7Ed217"

  let controlMap = new Map();
  
  const handleTransaction: HandleTransaction = async (
    txEvent: TransactionEvent
  ) => {
    const findings: Finding[] = [];
    
    const buyOrderDecreased = txEvent.filterLog(
        BuyOrderDecreasedEvent,
        NFT_MARKETPLACE_ADDRESS
    )
    const BuyOrderFullFilled = txEvent.filterLog(
        BuyOrderFullFilledEvent,
        NFT_MARKETPLACE_ADDRESS
    )
    
    buyOrderDecreased.forEach((_) => {
        controlMap.set('0x'+txEvent.transaction.data.slice(10,74), txEvent.block.number);
    })
    BuyOrderFullFilled.forEach((buyOrderFullfilledEvent) => {
        const { to, from, value } = buyOrderFullfilledEvent.args;
        
        if(controlMap.has('0x'+txEvent.transaction.data.slice(10,74)) && 
        controlMap.get('0x'+txEvent.transaction.data.slice(10,74)) == txEvent.block.number){
            findings.push(
                Finding.fromObject({
                  name: "SelltoOrderId frontrunning",
                  description: `Malicious actor decreased buy order with frontrunning!`,
                  alertId: "FORTA-1",
                  severity: FindingSeverity.Critical,
                  type: FindingType.Exploit,
                  metadata: {
                    to,
                    from,
                  },
                })
              );
        }
    });

    return findings;

  };
  
  
  export default {
    handleTransaction
  };
  