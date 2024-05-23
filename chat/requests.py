import requests


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
        print(f"  ERROR: API 요청 중 오류 발생: {e}")
        return None
    except KeyError as e:
        print(f"  ERROR: 응답에서 필요한 데이터를 찾을 수 없습니다: {e}")
        return None


def get_player_live(bno, bid):
    url = "https://live.afreecatv.com/afreeca/player_live_api.php"
    data = {
        "bid": bid,
        "bno": bno,
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
        response = requests.post(f"{url}?bjid={bid}", data=data)
        response.raise_for_status()  # HTTP 요청 에러를 확인하고, 에러가 있을 경우 예외를 발생시킵니다.
        res = response.json()

        CHDOMAIN = res["CHANNEL"]["CHDOMAIN"].lower()
        CHATNO = res["CHANNEL"]["CHATNO"]
        FTK = res["CHANNEL"]["FTK"]
        TITLE = res["CHANNEL"]["TITLE"]
        BJID = res["CHANNEL"]["BJID"]
        CHPT = str(int(res["CHANNEL"]["CHPT"]) + 1)

        return CHDOMAIN, CHATNO, FTK, TITLE, BJID, CHPT

    except requests.RequestException as e:
        print(f"  ERROR: API 요청 중 오류 발생: {e}")
        return None
    except KeyError as e:
        print(f"  ERROR: 응답에서 필요한 데이터를 찾을 수 없습니다: {e}")
        return None
