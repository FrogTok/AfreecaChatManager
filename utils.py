from pathlib import Path


def get_root_directory_path():
    # 파일 위치가 다른 디렉토리로 바뀌면 수정해야함
    return Path(__file__).parent.resolve()
