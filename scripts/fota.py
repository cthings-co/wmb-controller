"""WMB FOTA"""

import os
import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Final, cast

from smpclient import SMPClient
from smpclient.generics import SMPRequest, TEr1, TEr2, TRep, error, success
from smpclient.mcuboot import IMAGE_TLV, ImageInfo
from smpclient.requests.image_management import ImageStatesRead, ImageStatesWrite
from smpclient.requests.os_management import ResetWrite
from smpclient.transport.wirepas import SMPWirepasTransport

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    wmb_addr = int(os.environ.get('WMB_ADDRESS'))
    wmb_bin_path = os.environ.get('WMB_IMAGE')
    wmb_bin_hash: Final = ImageInfo.load_file(wmb_bin_path).get_tlv(
        IMAGE_TLV.SHA256
    )
    with open(wmb_bin_path, 'rb') as f:
        wmb_bin: Final = f.read()

    print("Connecting to WMB device...", end="", flush=True)
    async with SMPClient(SMPWirepasTransport(), wmb_addr) as client:
        print("OK")
        async def ensure_request(request: SMPRequest[TRep, TEr1, TEr2]) -> TRep:
            print("Sending request...", end="", flush=True)
            response = await client.request(request)
            print("OK")

            if success(response):
                return response
            elif error(response):
                raise Exception(f"Update Failed! Received error: {response}")
            else:
                raise Exception(f"Update Failed! Unknown response: {response}")

        response = await ensure_request(ImageStatesRead())
        if (response.images[0].hash == wmb_bin_hash.value):
            raise SystemExit("WMB device already updated! Exiting...")
        start_s = time.time()
        async for offset in client.upload(wmb_bin):
            print(
                f"\rUploaded {offset:,} / {len(wmb_bin):,} Bytes | "
                f"{offset / (time.time() - start_s) / 1000:.2f} KB/s           ",
                end="",
                flush=True,
            )

        response = await ensure_request(ImageStatesRead())
        assert response.images[1].hash == wmb_bin_hash.value
        assert response.images[1].slot == 1
        print("Confirmed the upload")
        print("Marking the new WMB firmware...")
        await ensure_request(ImageStatesWrite(hash=response.images[1].hash))
        print("Resetting for swap...")
        await ensure_request(ResetWrite())

        print("Waiting for WMB device to boot-up...")
        time.sleep(30)

        images = await ensure_request(ImageStatesRead())
        if success(images):
            assert images.images[0].hash == wmb_bin_hash.value
            assert images.images[0].slot == 0
            print("Update Successful!")
        elif error(images):
            raise SystemExit(f"Update Failed! Received error: {images}")
        else:
            raise SystemExit(f"Update Failed! Unknown response: {images}")


if __name__ == "__main__":
    asyncio.run(main())
