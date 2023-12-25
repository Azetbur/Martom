"""
import uasyncio as asyncio

async def handle_client(reader, writer):
    print("Client connected")
    await writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 80)
    async with server:
        await server.serve_forever()

# Run the event loop
asyncio.run(main())
"""

import uasyncio as asyncio

async def handle_echo(reader, writer):
    data = await reader.read(128)
    if (data):
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))
        print(type(data))

        message = ("HTTP/1.0 200 OK\r\n\r\nHello World \r\n")
        writer.write(message)
        await writer.drain()
    else:
        print("Close the client socket")
        writer.close()
        await writer.wait_closed()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '0.0.0.0', 80)
server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
