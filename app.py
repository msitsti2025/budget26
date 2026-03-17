import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="연구24 | 2026 국가 R&D 통합 대시보드", layout="wide")

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    # 정제된 파일 사용 (하이픈 제거된 버전)
    df = pd.read_csv('26-budget2_cleaned.csv')
    
    def clean_num(val):
        if pd.isna(val) or val == '' or val == '-': return 0.0
        # 천단위 콤마 제거 후 실수 변환
        return float(str(val).replace(',', ''))

    # 12대 전략기술 컬럼
    tech_cols = ['인공지능', '첨단바이오', '양자', '우주항공해양', '반도체/디스플레이', 
                 '첨단모빌리티', '첨단로봇제조', '차세대통신', '수소', '차세대원자력', '이차전지', '사이버보안']
    # 8대 정책분야 컬럼
    policy_cols = ['기초', '탄소중립', '국방', '출연직할', '재난안전', '지역', '기술사업화', '인력양성']
    
    # 모든 수치형 컬럼 정리
    target_cols = tech_cols + policy_cols + ['26년 예산']
    for col in target_cols:
        df[col] = df[col].apply(clean_num)
        
    # '번호(세부)'가 있는 행만 사용 (사업별 중복 합계 방지)
    summary_df = df[df['번호(세부)'].notnull()].copy()
    return summary_df, tech_cols, policy_cols

df, tech_cols, policy_cols = load_data()

# 3. 사이드바 설정 (모든 부처 기본 선택)
st.sidebar.title("🧬 연구24 분석도구")
all_ministries = sorted(df['부처명'].unique())  # 가나다순 정렬

# default 값을 전체 리스트(all_ministries)로 설정
selected_ministry = st.sidebar.multiselect(
    "분석 부처 선택", 
    options=all_ministries, 
    default=all_ministries
)

# 선택된 부처에 따라 데이터 필터링
filtered_df = df[df['부처명'].isin(selected_ministry)]

# 4. 메인 화면 구성
st.title("📊 2026 국가 R&D 예산 통합 대시보드")
st.markdown(f"현재 **{len(selected_ministry)}개** 부처의 데이터를 분석 중입니다.")

# 핵심 지표 (KPI)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("선택 부처 총 예산", f"{filtered_df['26년 예산'].sum():,.0f} 백만원")
with c2:
    # 필터링된 데이터 중 가장 큰 예산 기술 찾기
    top_tech = filtered_df[tech_cols].sum().idxmax()
    st.metric("최대 투자 기술", top_tech)
with c3:
    # 필터링된 데이터 중 가장 큰 예산 정책분야 찾기
    top_policy = filtered_df[policy_cols].sum().idxmax()
    st.metric("최대 투자 정책분야", top_policy)

# 탭 구성 (전략기술 vs 정책분야)
tab1, tab2 = st.tabs(["🎯 12대 전략기술별", "💡 8대 정책분야별"])

with tab1:
    col_a, col_b = st.columns(2)
    tech_totals = filtered_df[tech_cols].sum().reset_index()
    tech_totals.columns = ['기술', '예산']
    
    with col_a:
        fig_tech_bar = px.bar(tech_totals.sort_values('예산'), x='예산', y='기술', orientation='h', 
                             title="전략기술별 투자 규모", color='예산', color_continuous_scale='Viridis')
        st.plotly_chart(fig_tech_bar, use_container_width=True)
    with col_b:
        fig_tech_pie = px.pie(tech_totals, values='예산', names='기술', title="전략기술 예산 비중", hole=0.4)
        st.plotly_chart(fig_tech_pie, use_container_width=True)

with tab2:
    col_c, col_d = st.columns(2)
    policy_totals = filtered_df[policy_cols].sum().reset_index()
    policy_totals.columns = ['정책분야', '예산']
    
    with col_c:
        fig_pol_bar = px.bar(policy_totals.sort_values('예산'), x='예산', y='정책분야', orientation='h', 
                            title="정책분야별 투자 규모", color='예산', color_continuous_scale='Magma')
        st.plotly_chart(fig_pol_bar, use_container_width=True)
    with col_d:
        fig_pol_pie = px.pie(policy_totals, values='예산', names='정책분야', title="정책분야 예산 비중", hole=0.4)
        st.plotly_chart(fig_pol_pie, use_container_width=True)

st.divider()

# 부처별 포트폴리오 차트
st.subheader("🏢 부처별 예산 포트폴리오 상세")
view_option = st.radio("보기 기준 선택", ["전략기술 기준", "정책분야 기준"], horizontal=True)

if view_option == "전략기술 기준":
    melted = filtered_df.melt(id_vars=['부처명'], value_vars=tech_cols, var_name='기술', value_name='예산')
    stack_color = '기술'
else:
    melted = filtered_df.melt(id_vars=['부처명'], value_vars=policy_cols, var_name='정책분야', value_name='예산')
    stack_color = '정책분야'

fig_stack = px.bar(melted, x='부처명', y='예산', color=stack_color, barmode='stack', height=600)
st.plotly_chart(fig_stack, use_container_width=True)

# 데이터 상세 테이블
with st.expander("📝 필터링된 원본 데이터 보기"):
    st.dataframe(filtered_df)
