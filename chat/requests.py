import requests
import traceback
from dto import Bj, Broadcast


def request_bj(bid) -> Bj:
    url = f"https://st.afreecatv.com/api/get_station_status.php?szBjId=${bid}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 요청 에러를 확인하고, 에러가 있을 경우 예외를 발생시킵니다.
        res = response.json()

        result = res["RESULT"]
        if result and result == 1:
            bj = Bj(id=bid, **res["DATA"])
            return bj
        return None

    except requests.RequestException as e:
        tb = traceback.format_exc()
        print(f"  ERROR: API 요청 중 오류 발생: {e}\n {tb}")
        return None
    except KeyError as e:
        tb = traceback.format_exc()
        print(f"  ERROR: 응답에서 필요한 데이터를 찾을 수 없습니다: {e}\n {tb}")
        return None


def get_bno(bid):
    url = f"https://bjapi.afreecatv.com/api/{bid}/station"
    headers = {
        # 브라우저로만 접속할수있게 제한한듯? 이거 없으면 404에러뜸
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        # 필요한 경우 다른 헤더도 추가
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        # "Accept-Language": "en-US,en;q=0.5",
        # "Accept-Encoding": "gzip, deflate, br",
        # "Connection": "keep-alive",
        # "Upgrade-Insecure-Requests": "1",
        # "Referer": "https://example.com/",
        # "Cookie": "your_cookie_here",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 요청 에러를 확인하고, 에러가 있을 경우 예외를 발생시킵니다.
        res = response.json()

        broad = res["broad"]
        if broad:
            return broad["broad_no"]
        return None

    except requests.RequestException as e:
        tb = traceback.format_exc()
        print(f"  ERROR: API 요청 중 오류 발생: {e}\n {tb}")
        return None
    except KeyError as e:
        tb = traceback.format_exc()
        print(f"  ERROR: 응답에서 필요한 데이터를 찾을 수 없습니다: {e}\n {tb}")
        return None


def reqest_broadcast(broad_no: int, bj_id: str):
    url = "https://live.afreecatv.com/afreeca/player_live_api.php"
    data = {
        "bid": bj_id,
        "bno": broad_no,
        "type": "live",
        "confirm_adult": "true",
        "player_type": "html5",
        "mode": "landing",
        "from_api": "0",
        "pwd": "",
        "stream_type": "common",
        "quality": "HD",
    }

    try:
        response = requests.post(f"{url}?bjid={bj_id}", data=data)
        response.raise_for_status()  # HTTP 요청 에러를 확인하고, 에러가 있을 경우 예외를 발생시킵니다.
        res = response.json()
        broadcast = Broadcast(
            broad_no=broad_no,
            CHDOMAIN=res["CHANNEL"]["CHDOMAIN"].lower(),
            CHATNO=res["CHANNEL"]["CHATNO"],
            FTK=res["CHANNEL"]["FTK"],
            TITLE=res["CHANNEL"]["TITLE"],
            BJID=res["CHANNEL"]["BJID"],
            CHPT=str(int(res["CHANNEL"]["CHPT"]) + 1),
        )

        return broadcast

    except requests.RequestException as e:
        print(f"  ERROR: API 요청 중 오류 발생: {e}")
        return None
    except KeyError as e:
        print(f"  ERROR: 응답에서 필요한 데이터를 찾을 수 없습니다: {e}")
        return None


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()  # 요청에 실패하면 예외를 발생시킴
    return response.content
