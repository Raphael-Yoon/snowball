# link4(동영상/컨텐츠 안내) 관련 데이터 및 함수

video_map = {
    'APD01': {
        'youtube_url': 'https://www.youtube.com/embed/8QqNfcO9NPI?si=x4nMkbfyFRyRi7jI&autoplay=1&mute=1',
        'img_url': None,
        'title': 'Access Program & Data',
        'desc': 'APD01 설명'
    },
    'APD02': {
        'youtube_url': 'https://www.youtube.com/embed/vfWdDOb11RY?si=Nv-PDzWCD4hmi2Ja&autoplay=1&mute=1',
        'img_url': None,
        'title': 'Access Program & Data',
        'desc': 'APD02 설명'
    },
    'APD03': {
        'youtube_url': 'https://www.youtube.com/embed/2cAd2HOzICU?si=ZNXR_u8uAjWIsUd6&autoplay=1&mute=1',
        'img_url': None,
        'title': 'Access Program & Data',
        'desc': 'APD03 설명'
    },
    'PC01': {
        'youtube_url': 'https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal&autoplay=1&mute=1',
        'img_url': '/static/img/PC01.jpg',
        'title': '프로그램 변경 승인',
        'desc': '프로그램 변경 필요시 적절한 승인권자의 승인을 득합니다.'
    },
    'CO01': {
        'youtube_url': 'https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal&autoplay=1&mute=1',
        'img_url': '/static/img/CO01.png',
        'title': '배치잡 스케줄 등록 승인',
        'desc': '배치잡 스케줄 등록 시 적절한 승인권자의 승인을 득합니다.'
    },
    'OVERVIEW': {
        'youtube_url': 'https://www.youtube.com/embed/8ZnUo41usRk?si=8vkxW6vENB-689GV&autoplay=1&mute=1',
        'img_url': None,
        'title': '내부회계관리제도 Overview',
        'desc': '내부회계관리제도 개요 영상'
    },
    'PW': {
        'youtube_url': 'https://www.youtube.com/embed/0zpXQNFBHOI?si=v-BPoHFtzi4mhnUs&autoplay=1&mute=1',
        'img_url': None,
        'title': '패스워드 기준',
        'desc': 'ITGC 패스워드 기준 영상'
    },
    'PW_DETAIL': {
        'youtube_url': 'https://www.youtube.com/embed/-TjiH1fR5aI?si=nTj52Jzfz_XRKfZB&autoplay=1&mute=1',
        'img_url': None,
        'title': '패스워드 기준 상세',
        'desc': 'ITGC 패스워드 기준 심화 영상'
    },
    'MONITOR': {
        'youtube_url': 'https://www.youtube.com/embed/gT0g192562I?si=YU5Tz_tTpSDfj_Q8&autoplay=1&mute=1',
        'img_url': None,
        'title': '데이터 변경 모니터링',
        'desc': 'ITGC 데이터 변경 모니터링 통제 논의'
    },
    'DDL': {
        'youtube_url': 'https://www.youtube.com/embed/3K9GSKSSwxs?si=iOK746wefUzevGbo&autoplay=1&mute=1',
        'img_url': None,
        'title': 'DDL',
        'desc': 'DDL 관련 영상'
    },
    'ITPWC01': {
        'youtube_url': 'https://www.youtube.com/embed/bgSEzVWXp54?si=-biqR9k8bKaD-Pcv&autoplay=1&mute=1',
        'img_url': None,
        'title': 'ITGC In-Scope',
        'desc': 'ITGC In-Scope 기준'
    },
}

def get_link4_content(content_type):
    if not content_type or content_type not in video_map:
        return None
    return video_map[content_type] 