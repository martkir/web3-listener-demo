import asyncio
import json
import websockets
import click
from datetime import datetime


async def connect(chain):
    table_name_map = {
        "eth": "eth_dex_trades",
        "base": "base_dex_trades",
    }
    table_name = table_name_map[chain]
    uri = "wss://api.syve.ai/v1/ws"
    try:
        async with websockets.connect(uri) as ws:
            subscription_data = {"method": "subscribe", "table": table_name}
            await ws.send(json.dumps(subscription_data))
            while True:
                data_json = await ws.recv()
                try:
                    records = json.loads(data_json).get("success", {}).get("records", [])
                    for r in records:
                        block_number = r["block_number"]
                        trader_address = r["trader_address"]
                        token_symbol = r["token_symbol"]
                        amount_usd = f"${r['amount_usd']:,.2g}".ljust(10)
                        msg =  f"[{datetime.now()}] [Block-{block_number}] {trader_address} {amount_usd} {token_symbol}"
                        print(msg)
                except Exception as e:
                    print(str(e))
                    pass
    except Exception as e:
        print(f"Error: {e}")


@click.command()
@click.option("--chain", default="eth")
def main(chain):
    if chain not in ["eth", "base"]:
        raise Exception(f"Invalid chain: {chain}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect(chain))


if __name__ == "__main__":
    main()
