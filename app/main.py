import os
import httpx
import base64
import logging
import logging.handlers
from asyncio import gather
from dotenv import load_dotenv
from fastapi import FastAPI, Response, HTTPException


logger_file = logging.handlers.TimedRotatingFileHandler(
    filename="py.log",
    when="midnight",
    interval=3,
    backupCount=5
)
formatter = logging.Formatter(
    fmt='[{asctime}] #{levelname:8} {filename}:{lineno} - {message}',
    style='{'
)
logger_file.setFormatter(formatter)
logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)
logger.addHandler(logger_file)


app = FastAPI()

load_dotenv()


def _get_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def build_optional_headers() -> dict[str, str]:
    profile_title = _get_env("PROFILE_TITLE") or _get_env("SUB_NAME")
    headers = {
        "profile-title": profile_title,
        "support-url": _get_env("SUPPORT_URL"),
        "profile-web-page-url": _get_env("PROFILE_WEB_PAGE_URL"),
        "announce": _get_env("ANNOUNCE"),
        "profile-update-interval": _get_env("PROFILE_UPDATE_INTERVAL"),
        "providerid": _get_env("PROVIDER_ID"),
    }
    return {key: value for key, value in headers.items() if value}


async def fetch_links() -> tuple[list[str], list[str]]:
    try:
        if os.getenv('LOCAL_MODE') == 'on':
            with open('configs.txt', encoding='utf-8') as file:
                lines = file.readlines()

        else:
            github_token = os.getenv('GITHUB_TOKEN')
            headers = {}
            if github_token:
                headers = {
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3.raw"
                }
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    os.getenv('CONFIG_URL'),
                    headers=headers,
                    timeout=6
                )
                response.raise_for_status()
                lines = response.text.splitlines()
            
        sub_links = [
            line.strip()
            for line in lines
            if line.strip().startswith('http')
        ]
        vless_links = [
            line.strip()
            for line in lines
            if line.strip().startswith('vless://')
        ]
            
        return sub_links, vless_links
    except httpx.HTTPStatusError as e:
        logger.critical(f"GitHub fetch error: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Config file not found"
        )
    except FileNotFoundError as e:
        logger.critical(e)
        raise e


async def fetch_subscription(
    client: httpx.AsyncClient,
    sub_link: str,
    sub_id: str
) -> bytes | None:
    try:
        sub = await client.get(f'{sub_link}{sub_id}', timeout=3)
        sub.raise_for_status()
        return base64.b64decode(sub.text)
    except httpx.HTTPError as e:
        logger.warning(f"Can't get subscription url from {sub_link}{sub_id}: {str(e)}")


async def merge_all(sub_links: list[str], vless_links: list[str], sub_id: str) -> bytes:
    async with httpx.AsyncClient() as client:
        decoded_subs = [
            fetch_subscription(client, sub_url, sub_id) 
            for sub_url in sub_links
        ]
        tmp = await gather(*decoded_subs)
        data = [x for x in tmp if x is not None]
        
        if not data and not vless_links:
            logger.error("No subscriptions or configurations available")
            raise HTTPException(
                status_code=500,
                detail="There is nothing to return"
            )
        elif not data:
            logger.warning("No subscriptions available")

        encoded_vless_links = [link.encode() for link in vless_links]
        merged_subs = b''.join(data)
        merged_configs = b'\n'.join(encoded_vless_links)

        return merged_subs + merged_configs


path = os.getenv('URL')


@app.get(f'/{path}/{{sub_id}}')
@app.get(f'/{path}')
async def main(sub_id: str = "") -> Response:
    sub_links, vless_links = await fetch_links()
    if not sub_links and not vless_links:
        logger.error("No subscriptions or configurations available")
        raise HTTPException(status_code=500, detail="There is nothing to return")
    
    result = await merge_all(sub_links, vless_links, sub_id)
    global_sub = base64.b64encode(result)

    headers = build_optional_headers()
    return Response(content=global_sub, media_type='text/plain', headers=headers)
