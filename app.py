import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="2026 국가 R&D 예산 대시보드", layout="wide")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    df = pd.read_csv('26-budget2_cleaned.csv')
    
    # 숫자 클리닝 함수
    def clean_num(val):
        if pd.isna(val) or val == '-': return 0.0
        return float(str(val).replace(',', ''))

    tech_cols = ['인공지능', '첨단바이오', '양자', '우주항공해양', '반도체/디스플레이', 
                 '첨단모빌리티', '첨단로봇제조', '차세대통신', '수소', '차세대원자력', '이차전지', '사이버보안']
    
    df['26년 예산'] = df['26년 예산'].apply(clean_num)
    for col in tech_cols:
        df[col] = df[col].apply(clean_num)
        
    # 요약 행만 필터링 (중복 방지)
    summary_df = df[df['번호(세부)'].notnull()].copy()
    return summary_df, tech_cols

df, tech_cols = load_data()

# 3. 사이드바 필터
st.sidebar.header("🔍 필터 설정")
selected_ministry = st.sidebar.multiselect("부처 선택", options=df['부처명'].unique(), default=df['부처명'].unique()[:5])

# 데이터 필터링
filtered_df = df[df['부처명'].isin(selected_ministry)]

# 4. 메인 대시보드
st.title("🚀 2026 국가 R&D 전략기술 예산 대시보드")
st.markdown("본 대시보드는 12대 국가전략기술에 배정된 예산안을 분석하여 시각화합니다.")

# 상단 요약 지표 (KPI)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 예산 규모", f"{df['26년 예산'].sum():,.0f} 백만원")
with col2:
    st.metric("선택 부처 예산", f"{filtered_df['26년 예산'].sum():,.0f} 백만원")
with col3:
    st.metric("최대 투자 기술", "인공지능(AI)")

st.divider()

# 차트 영역
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 전략기술별 예산 총액")
    tech_totals = filtered_df[tech_cols].sum().reset_index()
    tech_totals.columns = ['기술', '예산']
    fig1 = px.bar(tech_totals.sort_values('예산'), x='예산', y='기술', orientation='h', 
                  color='예산', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("🍰 기술별 예산 비중")
    fig2 = px.pie(tech_totals, values='예산', names='기술', hole=0.4,
                  color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("🏢 부처별 기술 투자 상세 (Stacked Bar)")
# Melt 데이터 생성
melted = filtered_df.melt(id_vars=['부처명'], value_vars=tech_cols, var_name='Technology', value_name='Budget')
fig3 = px.bar(melted, x='부처명', y='Budget', color='Technology', barmode='stack',
              title="부처별 전략기술 포트폴리오")
st.plotly_chart(fig3, use_container_width=True)

# 데이터 표 확인
if st.checkbox("전체 데이터 보기"):
    st.dataframe(filtered_df)
