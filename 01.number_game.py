import random
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="숫자 맞추기 게임",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일링
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
    .history-card {
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-weight: 600;
        font-size: 1.05rem;
    }
    .history-up {
        background-color: rgba(239, 68, 68, 0.12);
        border-left: 5px solid #ef4444;
        color: #dc2626;
    }
    .history-down {
        background-color: rgba(59, 130, 246, 0.12);
        border-left: 5px solid #3b82f6;
        color: #2563eb;
    }
    .history-correct {
        background-color: rgba(34, 197, 94, 0.15);
        border-left: 5px solid #22c55e;
        color: #16a34a;
    }
    .range-box {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 16px;
        border-radius: 14px;
        text-align: center;
        font-size: 1.25rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    </style>
""", unsafe_allow_html=True)


def init_game(max_range=100):
    """게임 상태를 초기화합니다."""
    st.session_state.max_range = max_range
    st.session_state.target_number = random.randint(1, max_range)
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.guess_history = []
    st.session_state.min_possible = 1
    st.session_state.max_possible = max_range
    st.session_state.last_message = None


# 세션 상태 초기화
if "target_number" not in st.session_state:
    init_game(100)

if "best_score" not in st.session_state:
    st.session_state.best_score = None

if "games_played" not in st.session_state:
    st.session_state.games_played = 0

# 사이드바 구성
with st.sidebar:
    st.header("⚙️ 게임 설정")
    selected_range = st.select_slider(
        "숫자 범위 선택",
        options=[50, 100, 200, 500],
        value=st.session_state.get("max_range", 100)
    )

    # 난이도/범위 변경 시 게임 초기화
    if selected_range != st.session_state.max_range:
        init_game(selected_range)
        st.rerun()

    if st.button("🔄 새 게임 시작", use_container_width=True, type="primary"):
        init_game(selected_range)
        st.rerun()

    st.divider()
    st.header("📊 통계")
    st.write(f"🎮 플레이한 총 게임: **{st.session_state.games_played}회**")
    if st.session_state.best_score is not None:
        st.write(f"🏆 최고 기록 (최저 시도): **{st.session_state.best_score}회**")
    else:
        st.write("🏆 최고 기록: **아직 없음**")

    st.divider()
    st.caption("🎯 숫자 맞추기 게임 | Streamlit Web App")

# 메인 UI 구성
st.title("🎉 숫자 맞추기 게임 (Streamlit)")
st.markdown("1부터 지정된 범위 사이의 비밀 숫자를 정답에 가깝게 맞춰보세요!")

# 대시보드 메트릭 카드
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🎯 목표 범위", value=f"1 ~ {st.session_state.max_range}")
with col2:
    st.metric(label="🔢 현재 시도 횟수", value=f"{st.session_state.attempts}회")
with col3:
    best_display = f"{st.session_state.best_score}회" if st.session_state.best_score is not None else "-"
    st.metric(label="🏆 최고 기록", value=best_display)

# 유효 추정 범위 안내 박스
st.markdown(
    f'<div class="range-box">💡 현재 추정 가능한 범위: {st.session_state.min_possible} ~ {st.session_state.max_possible}</div>',
    unsafe_allow_html=True
)

# 지난 입력 메시지 피드백 표시
if st.session_state.last_message:
    msg_type, msg_text = st.session_state.last_message
    if msg_type == "UP":
        st.warning(msg_text)
    elif msg_type == "DOWN":
        st.info(msg_text)

# 게임 진행 컨트롤
if not st.session_state.game_over:
    default_guess = int((st.session_state.min_possible + st.session_state.max_possible) // 2)
    default_guess = max(1, min(st.session_state.max_range, default_guess))

    with st.form(key="guess_form", clear_on_submit=True):
        guess_input = st.number_input(
            f"숫자를 입력하세요 (1 ~ {st.session_state.max_range}):",
            min_value=1,
            max_value=st.session_state.max_range,
            value=default_guess,
            step=1
        )
        submit_button = st.form_submit_button("숫자 제출 🚀", use_container_width=True)

    if submit_button:
        guess = int(guess_input)
        st.session_state.attempts += 1

        if guess < st.session_state.target_number:
            result_type = "UP"
            st.session_state.min_possible = max(st.session_state.min_possible, guess + 1)
            st.session_state.last_message = (
                "UP",
                f"📈 **UP!** {guess}보다 큰 숫자입니다. (시도 횟수: {st.session_state.attempts}회)"
            )
        elif guess > st.session_state.target_number:
            result_type = "DOWN"
            st.session_state.max_possible = min(st.session_state.max_possible, guess - 1)
            st.session_state.last_message = (
                "DOWN",
                f"📉 **DOWN!** {guess}보다 작은 숫자입니다. (시도 횟수: {st.session_state.attempts}회)"
            )
        else:
            result_type = "CORRECT"
            st.session_state.game_over = True
            st.session_state.games_played += 1
            st.session_state.last_message = None

            # 최고 기록 갱신 확인
            if (
                st.session_state.best_score is None
                or st.session_state.attempts < st.session_state.best_score
            ):
                st.session_state.best_score = st.session_state.attempts

            st.balloons()

        # 히스토리에 추가 (최신 항목이 위로 오도록)
        st.session_state.guess_history.insert(0, {
            "attempt": st.session_state.attempts,
            "guess": guess,
            "result": result_type
        })
        st.rerun()

else:
    # 정답 맞춤 (게임 완료) 상태
    st.success(f"🎊 **축하합니다! 정답입니다!** (정답: {st.session_state.target_number})")
    st.markdown(f"**총 {st.session_state.attempts}회** 만에 정답을 맞추셨습니다! 🎉")

    if st.session_state.best_score == st.session_state.attempts:
        st.info("🌟 **최고 기록 갱신!** 축하합니다!")

    if st.button("🎮 새 라운드 시작하기", type="primary", use_container_width=True):
        init_game(st.session_state.max_range)
        st.rerun()

# 입력 히스토리 출력
if st.session_state.guess_history:
    st.subheader("📜 입력 히스토리")
    for item in st.session_state.guess_history:
        att = item["attempt"]
        g_val = item["guess"]
        res = item["result"]

        if res == "UP":
            st.markdown(
                f'<div class="history-card history-up">#{att}회차 | 입력: {g_val} 👉 📈 UP (더 큰 숫자입니다)</div>',
                unsafe_allow_html=True
            )
        elif res == "DOWN":
            st.markdown(
                f'<div class="history-card history-down">#{att}회차 | 입력: {g_val} 👉 📉 DOWN (더 작은 숫자입니다)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="history-card history-correct">#{att}회차 | 입력: {g_val} 👉 🎊 정답!</div>',
                unsafe_allow_html=True
            )
